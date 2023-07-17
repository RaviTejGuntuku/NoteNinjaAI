import openai
import math
from dotenv import load_dotenv
import os

class GenerateNotes:

    def __init__(self, transcription_file="", transcription_text="", generateFile=False):

        load_dotenv()

        openai.api_key = os.getenv("OPENAI_SECRET_KEY")

        if transcription_file != None and transcription_file != "":
            self.transcription_text = self.getTranscriptionText(transcription_file)
        
        elif transcription_text != None and transcription_text != "":
            self.transcription_text = transcription_text

        else:
            raise TypeError("Needed three arguments, but only two provided")

        self.summary_text = self.getSummary()

        self.notes_text = ""

        main_topics = self.identifyMainTopics(self.summary_text)

        self.notes_text += self.getLectureTitle(self.summary_text) + "\n\n"
        self.notes_text += self.getGeneralBulletPoints(main_topics, 8, 10) + "\n\n"

        for i in range(0, len(main_topics)):
            topic = main_topics[i]
            self.notes_text += self.getCategoryBulletPoints(topic, 6, 10) + "\n\n"

        self.notes_text += "\n" + self.getKeyDefinitions(self.summary_text) + "\n\n"

        if generateFile:
            if ".txt" in transcription_file:
                transcription_file = transcription_file.replace(".txt", "")
            
            self.notes_file_path = transcription_file+"_notes.txt"

            notes_file = open(self.notes_file_path, "w")
            notes_file.write(self.notes_text)
        
    
    def getNotesText(self):
        return self.notes_text
    
    def getNotesFilePath(self):
        return self.notes_file_path

    def getTranscriptionText(self, file):

        transcript_file = open(file, "r")
        transcription_text = ""

        for i in transcript_file:
            if (i == "\n"):
                continue
            transcription_text += i

        transcript_file.close()

        return transcription_text

    def getSummary(self):
        length_of_transcription = len(self.transcription_text)

        max_char_length_api = 5500
        max_word_length_api = math.ceil(max_char_length_api / 3.1)

        transcription_fragments = []

        for char in range(1, math.ceil(length_of_transcription / max_char_length_api) + 1):

            if (int(max_char_length_api) * char >= length_of_transcription):
                text_fragment = self.transcription_text[max_char_length_api *
                                                (char - 1): length_of_transcription]
            else:
                text_fragment = self.transcription_text[max_char_length_api *
                                                (char - 1): max_char_length_api * char]

            transcription_fragments.append(text_fragment)

        summary_text = ""

        for fragment in transcription_fragments:
            summary_text += self.summarize(fragment, math.ceil(max_word_length_api /
                              len(transcription_fragments))) + "\n"

        return summary_text


    def summarize(self, transcript, word_limit, tolerance=15):

        response = openai.Completion.create(
            model="text-davinci-003",
            prompt="""

            In paragraph form, write some of the main ideas, specific examples of the main ideas, and definitions of key terms expressed in this transcription. Please write at least {min_words} but not more than {max_words}.

            """.format(max_words=word_limit+tolerance, min_words=word_limit-tolerance) + transcript,
            temperature=0.5,
            max_tokens=1000,
            frequency_penalty=0.0,
            presence_penalty=1
        )

        return response["choices"][0]["text"]


    def identifyMainTopics(self, text):

        gpt_main_topics_ask = openai.Completion.create(
            model="text-davinci-003",
            prompt="""

                What are 7 main topics of this text that, on a scale of 1-10 (with 10 being the highest and 1 being the lowest), 
                have a high relevance that is based on the frequency in which they are mentioned/alluded to in the text 
                (organize them in a comma-seperated list)? Do NOT include the relevance rating in the output
                
                """+text,
            temperature=0.0,
            max_tokens=1000,
            frequency_penalty=0.0,
            presence_penalty=1
        )

        text_topics = gpt_main_topics_ask["choices"][0]["text"]

        text_topics = text_topics.replace("\n", "")

        text_topics = text_topics.replace(
            "The seven main topics of this text, in order of relevance, are: ", "")

        text_topics = text_topics.replace(
            "Seven main topics: ", "")

        text_topics = text_topics.replace(
            "Seven Main Topics: ", "")

        text_topics = text_topics.replace(
            "7 Main Topics: ", "")

        numbers_array = ["1", "2", "3", "4", "5", "6", "7", "8", "9"]

        for i in text_topics:
            if i in numbers_array:
                text_topics.replace(i, "")

        text_topics = text_topics.split(",")

        for i in range(0, len(text_topics)):
            item = text_topics[i]
            if (item[0] == " "):
                text_topics[i] = item[1:]
            if (item[len(item)-1] == " "):
                text_topics[i] = item[1:]

        text_topics = text_topics[0:7]
        # print(text_topics)
        return text_topics


    def getCategoryBulletPoints(self, topic, bullet_limit, verbosity):

        response = openai.Completion.create(
            model="text-davinci-003",
            prompt="""
            
            Based on the text below, jot down {bullets}-bullet points for the topic of 
            {topic}. Each bullet MUST NOT CONTAIN more than {words} words but should contain at least 6 words. 
            Include the topic as a header and the bullet points underneath the header

            """.format(topic=topic, bullets=bullet_limit, words=verbosity)+self.summary_text,
            temperature=0.5,
            max_tokens=1000,
            frequency_penalty=0.0,
            presence_penalty=1
        )

        return response["choices"][0]["text"]


    def getGeneralBulletPoints(self, main_topics, bullet_limit, verbosity):

        main_topics_string = ""

        for item in main_topics:
            main_topics_string += item
            if main_topics.index(item) != len(main_topics) - 1:
                main_topics_string += ","

        response = openai.Completion.create(
            model="text-davinci-003",
            prompt="""

            What are {bullets} details in this text that do NOT conform to these main topics --- {topics}? Include these details as bullet points, each with a maximum of {words} words, underneath the heading General Bullet Points:

            """.format(topics=main_topics_string, bullets=bullet_limit, words=verbosity)+self.summary_text,
            temperature=0.5,
            max_tokens=1000,
            frequency_penalty=0.0,
            presence_penalty=1
        )

        return response["choices"][0]["text"]


    def getKeyDefinitions(self, text):
        response = openai.Completion.create(
            model="text-davinci-003",
            prompt="""

            What are the definitions of the key terms covered in this summary? Base these definitions solely off of the text below. Include the key definitions below the heading, Key Definitions.

            """+text,
            temperature=0.0,
            max_tokens=1000,
            frequency_penalty=0.0,
            presence_penalty=1
        )

        return response["choices"][0]["text"]


    def getLectureTitle(self, text):
        response = openai.Completion.create(
            model="text-davinci-003",
            prompt="""

            Based on the summary below, what is the title of the lecture? ONLY OUTPUT THE TITLE AND NO PRECEDING OR FOLLOWING TEXT

            """+text,
            temperature=0.0,
            max_tokens=1000,
            frequency_penalty=0.0,
            presence_penalty=1
        )

        return response["choices"][0]["text"]

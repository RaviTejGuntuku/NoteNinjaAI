import transcribe_audio as ta
import note_taker as nt
import gradio as gr
import os

def notesGenFrontEnd(audio_input, transcription_input):

    transcription_text = ""

    audio_supplied = False
    transcription_supplied = False

    if (transcription_input == None or transcription_input == "") and (audio_input == None or audio_input == ""):
        raise gr.Error("Please supply media or transcription file")

    elif transcription_input == None or transcription_input == "":
        transcribe_object = ta.Transcribe(audio_input)
        transcription_text = transcribe_object.transcribe()
        audio_supplied = True
    
    elif audio_input == None or audio_input == "":
        transcription_file = open(transcription_input, "r")
        transcription_text = transcription_file.read()
        transcription_supplied = True
    
    else:
        raise gr.Error("Please supply EITHER a media file OR a transcription file, not both")
    
    notes_object = nt.GenerateNotes(transcription_text=transcription_text)

    notes_file_name = ""

    if (audio_supplied):
        notes_file_name = audio_input.rsplit(".", 1)[0]

    elif (transcription_supplied):
        notes_file_name = transcription_input.rsplit(".", 1)[0]

    notes_file = open(notes_file_name, "w")
    notes_file.write(notes_object.getNotesText())
    notes_file.close()

    return notes_file_name


with gr.Blocks(theme=gr.themes.Base(primary_hue="orange", secondary_hue = "pink"), title="ai_notes_generator") as demo:
    gr.Markdown("""
            <h1 style="text-align: center; font-family: \"Times New Roman\"">NoteNinjaAI</h1>
            <p style="text-align: center;">Psst! Are you tired of listening to hour-long lectures and taking notes till your wrist hurts? 
                Or do you want the jist of a lesson you missed? <br/>
                Enter <b>NoteNinjaAI</b> - powered by OpenAI services, this program can transform a lecture audio or transcription into structured notes, containing main topics followed by subbullets; general bullet points; and key definitions.
                <br>
                <br>
                Learn more about this application by visiting the <a href="https://github.com/RaviTejGuntuku/NoteNinjaAI"> GitHub Repository </a> </p>
            """)
    with gr.Row():
        with gr.Column():
            with gr.Tab("Notes from Media File"):
                media_input = gr.Audio(label="Upload Media File", type="filepath")
            
            with gr.Tab("Notes from Transcription"):
                transcription_input = gr.File(label="Upload Transcription File", type="file", file_types=["text"])

        output_file = gr.File(label="Notes Output")

    btn = gr.Button("Generate Notes", variant="primary")
    btn.click(fn=notesGenFrontEnd, inputs = [media_input, transcription_input], outputs = [output_file], api_name="generate_notes")

demo.launch()

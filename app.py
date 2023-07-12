from flask import Flask,request,render_template
from youtube_transcript_api import YouTubeTranscriptApi
from transformers import pipeline # type: ignore
from googletrans import Translator

app= Flask(__name__)


@app.get('/summary')
def summary_api():
    url=request.args.get('url','')
    global summary
    video_id= url.split("=")[1]
    transcript = get_transcript(video_id)
    translated_text = translate_text(transcript)
    summary = get_summary(translated_text)
    return summary


@app.route('/translate',methods=['GET','POST'])
def translate():
    target="en"
    translator=Translator()
    if request.method == 'POST':
         target=request.form['language']
    #print(target)
    result=translator.translate(summary,src="en",dest=str(target))
    return render_template('translation.html',result=result.text)


def get_transcript(video_id):
    transcript_list=YouTubeTranscriptApi.get_transcript(video_id)
    transcript=' '.join([d['text'] for d in transcript_list])
    return transcript


def translate_text(text):
    translator = Translator()
    translation = translator.translate(text, dest='en')
    return translation.text


def get_summary(transcript):
    max_length=86
    summary=''
    summariser=pipeline("summarization",model="t5-small")
    for i in range(0,(len(transcript)//1000)+1):
        summary_text=summariser(transcript[i*1000:(i+1)*1000],max_length=max_length)[0]['summary_text']
        summary=summary+summary_text+' '
    return summary


if __name__=='__main__':
    app.run()

import modal
from youtube_transcript_api import YouTubeTranscriptApi
from modal import Image, Stub, wsgi_app


bot_image = modal.Image.debian_slim().pip_install("openai")
bot_image = bot_image.pip_install("numpy")
bot_image = bot_image.pip_install("pandas")
bot_image = bot_image.pip_install("youtube_transcript_api")
bot_image = bot_image.pip_install("flask")
bot_image = bot_image.pip_install("flask_cors")

stub = modal.Stub("activeLearnEndpoints", image=bot_image)


def break_into_chunk(transcript_chunks, left_index, right_index):
    current_chunk = ""
    for i in range(left_index, right_index):
        inner_dict = transcript_chunks[i]
        current_chunk += str(
            inner_dict['text'] + " Start Position: " + str(inner_dict['start']) + ", " + "End Position: " + str(
                inner_dict['start'] + inner_dict['duration']) + "\n")

    return current_chunk

@stub.function(secret=modal.Secret.from_name("my-openai-secret"))
def complete_text(prompt):
    from openai import OpenAI
    client = OpenAI()
    response = client.chat.completions.create(
        model="gpt-3.5-turbo-1106",
        messages=[
            {"role": "system", "content": "You are an instructor."},
            {"role": "user", "content": prompt},
        ]
    )
    return response.choices[0].message.content


@stub.function(image=bot_image)
@wsgi_app()
def flask_app():
    from flask import Flask, request
    from flask_cors import CORS
    from youtube_transcript_api import YouTubeTranscriptApi

    web_app = Flask(__name__)
    CORS(web_app)

    @web_app.post("/echo")
    def home():
        video_id = request.get_data().decode('utf-8')

        print("here: \n")
        print(video_id)

        transcript_chunks = YouTubeTranscriptApi.get_transcript(video_id, preserve_formatting=True)

        number_of_elements = len(transcript_chunks)

        first_chunk = break_into_chunk(transcript_chunks, 0, number_of_elements // 5)
        second_chunk = break_into_chunk(transcript_chunks, number_of_elements // 5, (number_of_elements * 2) // 5)
        third_chunk = break_into_chunk(transcript_chunks, (number_of_elements * 2) // 5, (number_of_elements * 3) // 5)
        fourth_chunk = break_into_chunk(transcript_chunks, (number_of_elements * 3) // 5, (number_of_elements * 4) // 5)
        fifth_chunk = break_into_chunk(transcript_chunks, (number_of_elements * 4) // 5, number_of_elements)

        question_prompt = """I'm going to give you a transcript with start and end positions. I would like you to give me the numerical value of the last End Position in this transcript. Then give me a question with four multiple choice questions you would ask at that position. Focus on the "Analyze" component of bloom's taxonomy and try to get students to synthesize ideas more complexly when they answer these questions. Please be extremely careful to make the questions at a given position make sense with a viewer only having the knowledge from that timestamp and previous timestamps, not any information after that timestamp.
        Transcript: \n"""

        # implement threading here for 5x faster response time
        first_response = complete_text.remote(question_prompt + first_chunk)
        second_response = complete_text.remote(question_prompt + second_chunk)
        third_response = complete_text.remote(question_prompt + third_chunk)
        fourth_response = complete_text.remote(question_prompt + fourth_chunk)
        fifth_response = complete_text.remote(question_prompt + fifth_chunk)

        prompt_two = """I need you to take the following of questions and output/clean the response into the following format: 
            \"Timestamp in float\" - \"Question\" - \"Answer Choice A\" - \"Answer Choice B\" - \"Answer Choice C\" - 
            \"Answer Choice D\" - \"Correct Answer\" Please say absolutely nothing besides doing this reformatting. Ok, 
            here is are the questions: \n""" + "Question 1: " + first_response + "\n" + "Question 2: " + second_response + "\n" + \
                     "Question 3: " + third_response + "\n" + "Question 4: " + fourth_response + "\n" + "Question 5: " + fifth_response + "\n"

        return complete_text.remote(prompt_two)


    return web_app

# torch.set_default_device("cuda")

# model = AutoModelForCausalLM.from_pretrained("microsoft/phi-1", torch_dtype="auto", trust_remote_code=True)
# tokenizer = AutoTokenizer.from_pretrained("microsoft/phi-1", trust_remote_code=True)

# inputs = tokenizer('''def print_prime(n):
#   """
#   Print all primes between 1 and n
#   """''', return_tensors="pt", return_attention_mask=False)

# outputs = model.generate(**inputs, max_length=200)
# text = tokenizer.batch_decode(outputs)[0]
# print(text)



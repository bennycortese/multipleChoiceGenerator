import modal
from modal import Stub, web_endpoint

bot_image = modal.Image.debian_slim().pip_install("openai")
bot_image = bot_image.pip_install("numpy")
bot_image = bot_image.pip_install("pandas")
bot_image = bot_image.pip_install("youtube_transcript_api")

stub = modal.Stub("activeLearnEndpoints", image=bot_image)


@stub.function(secret=modal.Secret.from_name("my-openai-secret"))
def complete_text(prompt):
    from openai import OpenAI
    client = OpenAI()
    response = client.chat.completions.create(
        model="gpt-4-1106-preview",
        messages=[
            {"role": "system", "content": "You are an instructor."},
            {"role": "user", "content": prompt},
        ]
    )
    return response.choices[0].message.content


@stub.function()
@web_endpoint()
def main():
    from youtube_transcript_api import YouTubeTranscriptApi
    transcript_chunks = YouTubeTranscriptApi.get_transcript("2E0GHyz4Hk0", preserve_formatting=True)
    big_transcript = ""
    for inner_dict in transcript_chunks:
        big_transcript += str(
            inner_dict['text'] + " Start Position: " + str(inner_dict['start']) + ", " + "End Position: " + str(
                inner_dict['start'] + inner_dict['duration']) + "\n")

    prompt_one = """I'm going to give you a transcript with start and end positions. I would like you to give me five end locations where you think asking a question to the listener would be the most appropriate, and then the question with four multiple choice questions you would ask at that position. Focus on the "Analyze" component of bloom's taxonomy and try to get students to synthesize ideas more complexly when they answer these questions. Please be extremely careful to make the questions at a given position make sense with a viewer only having the knowledge from that timestamp and previous timestamps, not any information after that timestamp.
Transcript: \n""" + big_transcript


    first_response = complete_text.remote(prompt_one)

    prompt_two = """I need you to take the following text and output/clean the response into the following format: 
    \"Timestamp in float\" - \"Question\" - \"Answer Choice A\" - \"Answer Choice B\" - \"Answer Choice C\" - 
    \"Answer Choice D\" - \"Correct Answer\" Please say absolutely nothing besides doing this reformatting. Ok, 
    here is the text: \n""" + first_response

    return complete_text.remote(prompt_two)

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


# Press the green button in the gutter to run the script.

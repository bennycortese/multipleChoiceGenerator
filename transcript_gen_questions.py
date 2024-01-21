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
        model="gpt-3.5-turbo-1106", # note, test this with gpt-4 for quality improvements
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

        print(first_response)
        print(second_response)
        print(third_response)
        print(fourth_response)
        print(fifth_response)

        prompt_two = """I need you to take the following chunk of questions and output/clean the response into the following: 
            Timestamp in float "!" Question "!" Answer Choice A "!" Answer Choice B "!" Answer Choice C "!"
            Answer Choice D "!" Correct Answer "!". You can do this, I have seen you do it many times. In fact, the example I got was from you.
            
            Here is an example of what format I want you to output:
            
            331.44 "!" Based on the reactions of the cast members, what can you infer about the flavor of the dish they just tasted? "!" a) The dish tasted surprisingly pleasant, with a unique and enjoyable flavor profile. "!" b) The dish was extremely spicy, causing discomfort and numbness in the mouth and throat. "!" c) The dish had an overwhelming aroma but a mild taste, providing a confusing sensory experience. "!" d) The dish was well-received, leading to curiosity and questions about its ingredients and preparation. "!" A "!"
            623.7 "!" Based on the conversation up to this point, what conclusions can you draw about the experience of trying the food item and its impact on the participants? "!" a) The food item is generally well-received and enjoyable for most participants, with some initial hesitancy overcome by positive reactions. "!" b) The food item elicits mixed reactions, with some finding it tolerable and others expressing dislike or discomfort. "!" c) The food item has a polarizing effect, with some participants enjoying it immensely while others find it unappealing or repulsive. "!" d) The food item has had a clear, negative impact on the participants, with most expressing regret in trying it. "!" A "!"
            952.337 "!" What effect did the chaotic and unexpected turn of events have on the participants' reactions? "!" A. It added excitement and unpredictability to the experience, prompting heightened emotions and laughter among the participants. "!" B. It made the participants feel anxious and distressed, disrupting the balance of the activity. "!" C. It led to confusion and discomfort, causing the participants to struggle in managing the situation. "!" D. It created a sense of disengagement and dissatisfaction, resulting in a negative response from the participants. "!" A "!"
            1291.23 "!" Why might the presence of the balloon be significant in this context? "!" a) It was planted as a distraction to create a lighter mood in the room "!" b) It was an attempt to sabotage the birthday celebration "!" c) It could have symbolized a sense of unpredictability and lightheartedness "!" d) It was a sign of someone's attempt to be mischievous "!" C "!"
            1614.1100000000001 "!" Reflecting on the edible birthday gift, what does the transition in Shayne's feelings (from "it's gonna be bad" to "total dread") suggest about his experience with the gift? "!" a) Shayne's initial reaction to the gift was overly negative, and he did not give it a fair chance. "!" b) The unique layers of the gift inspired complex and mixed emotions for Shayne, demonstrating a deeper level of engagement with the experience. "!" c) Shayne's final reaction showed that he enjoyed the gift more than he initially thought, leading to a positive surprise. "!" d) The layers of the gift confused Shayne, making it difficult for him to truly appreciate the thoughtfulness behind it. "!" C "!"
             
            And here is another example:
            
            378.397 "!" What can you infer about the dynamics of the relationship between the characters based on their conversation at the wedding? Choose the best answer from the following options: "!" A) They have a deep emotional bond that goes beyond physical attraction. "!" B) Their conversation reveals shallow and superficial intentions. "!" C) The characters seem to be struggling with unresolved emotions from their past relationships. "!" D) The dialogue reflects a disconnection between their words and their true feelings. "!" A "!"
            758.865 "!" In this improv skit, the participants engage in a conversation that shifts from playful banter to more serious and personal themes. How does the progression of the conversation portray the performers' skill in improvisation and empathy? "!" a) The conversation never reaches a deeper level, staying within the realms of playful teasing and banter. "!" b) It showcases the performers' ability to smoothly transition from lighthearted joking to more serious and personal conversations, displaying strong improvisational skills. "!" c) The conversation becomes disjointed and confusing, making it difficult for the participants to effectively maintain the flow and coherence of the scene. "!" d) The participants fail to effectively engage with emotions or personal topics, revealing a lack of empathy and depth in their performance. "!" B "!"
            1102.6309999999999 "!" Based on the conversation at this point, what themes or commonalities can you identify in the interactions between the characters, and how do they contribute to the overall comedic value of the dialogue? "!" a) The use of inside jokes and shared experiences creates a sense of camaraderie and genuine enjoyment among the characters, enhancing the comedic value. "!" b) The constant repetition of affirmations and agreement between the characters adds a rhythm and pacing that amplifies the comedic timing and delivery. "!" c) The sudden shift in conversation topics and absurd scenarios inject surprise and unpredictability, adding an element of randomness that amplifies the comedic value. "!" d) The fluidity and interplay of conversational turns and interruptions create a conversational chaos that enriches the comedic dynamics and punchlines. "!" C "!"
            1470.952 "!" Which of the following best summarizes the different attitudes and behaviors expressed by the cast members in this segment? "!" A) Can you identify any patterns or recurring themes that are expressed through the dialogues in this segment? "!" B) How did the topics discussed evolve and change throughout the segment? "!" C) What implications can be drawn about the dynamics and relationships among the cast members from this segment? "!" D) How do the interactions and conversations in this segment reflect the overall theme of the skit? "!" A "!"
            1831.586 "!" Based on the witness testimony, what inference can you make about the events that took place in the courtroom? "!" A) The witnesses' stories contradict each other, making it difficult to determine the truth. "!" B) The witnesses' stories complement each other, providing a clear picture of the events that unfolded. "!" C) The witnesses' stories present a confusing and inconclusive narrative about the events. "!" D) The witnesses' stories reveal inconsistencies that raise doubt about the reliability of the testimonies. "!" D "!"
            
            And here is another example:
            
            541.92 "!" Considering the discussion about the viability rankings and changes in the meta, why might players start to question the effectiveness of certain Pokemon, such as Raiku, over time? "!" A) The introduction of new mechanics in the game that favored other Pokemon. "!" B) The shift in strategies and team compositions used by top players. "!" C) The rise in popularity of different playstyles, leading to different demands from Pokemon. "!" D) The development of counter strategies that rendered certain Pokemon less effective in the meta. "!" D "!"
            1047.439 "!" Based on the discussion about using cloyster and fortress on different teams and the effectiveness of cloyster's speed and lack of crippling fire resistance, which factor or factors contribute to cloyster's versatility on various team types? "!" A) Its ability to outspeed and threaten certain offensive threats, as well as its capability to fit onto both offense and stall teams. "!" B) Its potential to set up spikes early in the game and its resistance to various status moves. "!" C) Its capacity to counter specific Pokemon like snorlax and machamp and its ability to explode on those counters. "!" D) Its speed and its stat-specific resistance to moves like surf and explosion. "!" A "!"
            1520.4 "!" How has the perspective on spikes in the Pokémon metagame changed over time? "!" A) The use of spikes has decreased significantly in recent years. "!" B) Players in the past considered spikes to be less important compared to modern players. "!" C) The type of strategies associated with spikes has evolved over time. "!" D) The influence of spikes on team composition has remained consistent from past to present. "!" C "!"
            2057.04 "!" What patterns and trends can you infer from the usage statistics of GSC Pokemon, particularly focusing on the prevalence and effectiveness of Cloyster in the metagame? "!" a) Cloyster consistently shows high usage and performance compared to Raikou across multiple years in GSC competitive play. "!" b) Raikou has remained a consistent and powerful presence in GSC, often outperforming Cloyster in usage and wins. "!" c) Usage statistics reveal that Cloyster struggles to maintain relevance and impact in the rapidly evolving GSC metagame. "!" d) The usage statistics suggest that Cloyster has experienced fluctuating levels of popularity and success over the years, with different trends in each season. "!" D "!"
            2562.64 "!" In the given meta game, what factors have contributed to Cloyster's rise in ranking compared to Raikou? "!" a) The increased usage of earthquake moves by opponents "!" b) Cloyster's ability to facilitate its teammates and function as a threat on its own "!" c) Gengar's reduced popularity in the meta game "!" d) The changes to the fundamental basis of the old metagame "!" B "!"
            
            Please say absolutely nothing besides doing this reformatting. Only print the response in the format as shown in the examples. 
            Ok, here is are the questions: \n""" + "Question 1: " + first_response + "\n" + "Question 2: " + second_response + "\n" + \
                     "Question 3: " + third_response + "\n" + "Question 4: " + fourth_response + "\n" + "Question 5: " + fifth_response + "\n"


        

        actual_return_data = complete_text.remote(prompt_two)

        print(actual_return_data)
        return actual_return_data

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



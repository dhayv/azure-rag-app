---
source: "https://stackoverflow.com/questions/78395237/query-azure-openai-with-images"
title: "Query @azure/openai with images?"
topic: ["openai-api", "azure-openai"]
captured_at: "2025-08-11"
license: "CC BY-SA 4.0"
attribution: "Stack Overflow users: meds (asker), Lee-xp"
---

# RAW_THREAD

Query @azure/openai with images?

Asked Apr 27, 2024 at 13:59 • Modified 1 year, 1 month ago • Viewed 4k times

Score: 1

On chat.openai.com I can upload an image and ask chatgpt a question about it, with the existing openai and @azure/openai api however there doesn't seem to be a way to do this? The ChatCompletion object in both cases only take text prompts.

Is this feautre supported at an api level?

Tags: openai-api • azure-openai

1 Answer
Answer 1
Score: 5 • Answered Apr 27, 2024 at 17:04 by Lee-xp • Edited Jun 13, 2024 at 14:00

With OpenAI you just include your image as part of the message that you supply. Here is a piece from the code I use, which works whether you have an image or not:

python
Copy code
if image != '':
    # Get base64 string
    base64_image = encode_image(image)
    content = [
        {
            "type": "text",
            "text": your_prompt
        },
        {
            "type": "image_url",
            "image_url": {
                "url": f"data:image/jpeg;base64,{base64_image}"
            }
        }
    ]
else:
    content = your_prompt
messages.append({"role": "user", "content": content})
And then

python
Copy code
payload = {
    "model": model_name,
    "temperature": temperature,
    "max_tokens": tokens,
    "messages": messages
}
where encode_image() is defined:

python
Copy code
def encode_image(image_path):
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')
Currently you need to target OpenAI model gpt-4-vision-preview. Update: As @Michael suggests, it also works with gpt-4o.

Comments

Thanks for the help! Curious can it just be a remote url or does it have to be a base64 embedded image? — meds • Apr 28, 2024 at 1:22

Glad to help. Yes you can use the URL to an image online with "url": "https: . . . " — Lee-xp • Apr 28, 2024 at 9:08

This implementation also works perfectly with GPT-4o. — Michael Kemmerzell • Jun 13, 2024 at 9:13

@meds - I'm just wondering - since the accepted answer just deals with openai (not Azure) it would probably be useful to change the question title to: 'Query openai with images?' … — Lee-xp • Jun 14, 2024 at 12:24

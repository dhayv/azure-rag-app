---
source: "https://stackoverflow.com/questions/76611348/azure-openai-bring-your-own-data-feature-not-providing-correct-answers"
title: "Azure OpenAI 'Bring Your Own Data' Feature Not Providing Correct Answers"
topic: ["azure-cognitive-search", "openai-api", "azure-openai"]
captured_at: "2025-08-11"
license: "CC BY-SA 4.0"
attribution: "Stack Overflow users: Kaja Sherief (asker), Ranran Wang, Tom, joao8tunes"
---

# RAW_THREAD

Azure OpenAI 'Bring Your Own Data' Feature Not Providing Correct Answers

Asked Jul 4, 2023 at 9:49 • Modified 1 year, 10 months ago • Viewed 2k times
Part of Microsoft Azure Collective

Score: 3

I've been using Azure's OpenAI and the 'Bring Your Own Data' (BYOD) feature for a while now. Recently, I've encountered an issue where the BYOD feature is not providing the correct answers to certain queries.

When I input the same question into the Azure Cognitive Search Explorer, it successfully returns the correct matches. However, when I pose the same question to the BYOD feature, it responds with "I don't have information about this."

I've double-checked my data and it seems to be correctly formatted and uploaded. I'm not sure why the BYOD feature isn't able to retrieve the correct information.

Has anyone else encountered this issue? Any suggestions on how to troubleshoot and fix this problem would be greatly appreciated.

Tags: azure-cognitive-search • openai-api • azure-openai

Comments

refer this Azure OpenAI — 'Bring Your Own`Data (links)* — Sampath • Jul 5, 2023 at 14:10

I had a similar problem … recommend you to write an script to pre-process the input files and split it in one-page chunks … limitation in the number of prompt characters that may truncate the answers… — Playing With BI • Aug 15, 2023 at 6:35

3 Answers
Answer 1
Score: 0 • Answered Jul 5, 2023 at 21:16 by Ranran Wang

Few things to try:

Did you turn on "Semantic Search" which will help with the results?

Sometimes asking the same question again will help get the correct answer.

You mentioned you run into the issue with "certain queries", did you notice some pattern of these queries?

Comments

If none of them helps, please contact to Microsoft Support and we can work with you to see your issue deeply — Ranran Wang • Jul 5, 2023 at 21:17

Yes, I have turned on Semantic Search… Search Explorer returns the correct answer… BYOD fails — Kaja Sherief • Jul 7, 2023 at 10:09

Answer 2
Score: 0 • Answered Jul 6, 2023 at 0:40 by Tom

You could use Marqo as your information source and pair it directly with GPT instead. This would give you a lot more control. Here's an example of augmented retrieval with BYOD on Marqo: (link)

Answer 3
Score: 0 • Answered Oct 6, 2023 at 14:21 by joao8tunes

I have a GitHub project that allows for integrating external data with LLM without the need for model retraining. It also enables a side-by-side comparison of Azure/OpenAI and GCP PaLM technologies. (link)


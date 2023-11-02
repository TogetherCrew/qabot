#  Author Ene SS Rawa / Tjitse van der Molen

# # # # # import libraries # # # # #

import openai
import tiktoken
from .call_GPT import call_GPT, split_prompt_tokens


def summarize_text(text_input, OA_key, include_identifier, text_type,
                   gpt_command="Make a one paragraph summary in english of the most important points from this "):
    """
	Summarizes text from dictionary through a GPT API call
	
	Input:
	text_input - {str:str}: dictionary with text to summarize. Keys are 
		strings containing the text index and optionally an additional
		identifier. The values are strings containing the text to be
		summarized. At least one key-value pair is required.
	OA_key - str: OpenAI key for API call
	include_identifier - bool: whether identifier in dictionary key 
		should be included when making the summary
	text_type - str: type of text for summary (included in prompt)
	gpt_command - str: the command for GPT, forming the base of the prompt.
    	This variable is not intended to be changed from its default

	Output:
	summary_out - str: summary of merged text in text_input with a
		maximum length of 500 tokens
	token_counter - int: number of tokens used for the processing

	Notes:
	If the text to be summarized and prompt combined are longer than 
	3490 tokens, the text will be split into smaller parts that are 
	summarized individually and afterwards a summary is made of the 
	summaries from smaller parts
	"""

    # # # PREPARATIONS # # #

    # set the provided OA_key
    openai.api_key = OA_key

    # set token counter to 0
    token_counter = 0

    # # # ORGANIZE DATA INTO PROMPT # # #

    # define prompt bases for summarizing
    summarize_prompt_basis = gpt_command + text_type + ":\n\n"

    # initiate gpt prompt with basis
    gpt_prompt = summarize_prompt_basis

    # for each message in text_input
    for mess_i in text_input.keys():

        # if message identifier should be included
        if include_identifier:

            # include complete identifier as message index text
            mess_index_text = mess_i + ": "

        else:

            # extract index number as message index text
            str_split = mess_i.split(":")
            mess_index_text = str_split[0] + ": "

        # add message index text and message content to gpt_prompt
        gpt_prompt = gpt_prompt + mess_index_text + text_input[mess_i] + "\n"

    # # # CHECK NUMBER OF TOKENS # # #

    # split prompt based on number of tokens
    prompt_list = split_prompt_tokens(gpt_prompt, 3500, summarize_prompt_basis)

    # exit if prompt was too long and could not be split
    if not prompt_list:
        return None, 0

    # # # SUMMARIZE # # #

    # initiate summary out
    summary_out = []

    # for each split prompt
    for final_prompt in prompt_list:
        # summarize
        prompt_summary, num_tokens_used = call_GPT(final_prompt,
                                                   gpt_role="You are a helpful assistant with a PhD in modern English literature.")

        # store results
        summary_out.append(prompt_summary)

        # add used tokens to token counter
        token_counter += num_tokens_used

    # # # MERGE SUMMARIES # # #

    # as long as prompt got split
    while len(summary_out) > 1:

        # define new prompt basis for merging summaries
        merge_summaries_prompt_basis = "A long {} was summarized by GPT in smaller chunks to stay within the token limit. Merge the summaries into a single one paragraph summary in English containing only the most important information.\n\n".format(
            text_type)

        # initiate merge summaries prompt with basis
        merge_summaries_prompt = merge_summaries_prompt_basis

        # for each summary to be merged
        for merge_sum in summary_out:
            # add summary to prompt
            merge_summaries_prompt = merge_summaries_prompt + merge_sum + "\n\n"

        # split prompt based on number of tokens
        prompt_list_merge = split_prompt_tokens(merge_summaries_prompt, 3490, merge_summaries_prompt_basis)

        # remove old values from summary out
        summary_out = []

        # for each split prompt
        for final_prompt in prompt_list_merge:
            # summarize
            prompt_summary, num_tokens_used = call_GPT(final_prompt,
                                                       gpt_role="You are a helpful assistant with a PhD in modern English literature.")

            # store results
            summary_out.append(prompt_summary)

            # add used tokens to token counter
            token_counter += num_tokens_used

    return summary_out[0], token_counter

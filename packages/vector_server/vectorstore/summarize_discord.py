#  Author Ene SS Rawa / Tjitse van der Molen

# # # # # import libraries # # # # #

from .summarize_text import summarize_text


def summarize_discord_main(mess_dict_all, OA_key, summarize_channel, summarize_server):
	"""
	Summarizes messages in discord server, channel and thread
	
	Input:
	mess_dict_all - {str:{str:{str:str}}}: dictionary with server channel
		names as keys and dictionaries as values. Each of these dictionaries
		has thread names as keys and dictionaries as values. Each of these
		dictionaries has message indices and optional account names as
		keys and message contents as values.
	OA_key - str: OpenAI key for API call
	summarize_channel - bool: whether channel level summaries should be 
		made
	summarize_server - bool: whether server level summary should be made
		(requires summarize_channel to be True)
	
	Output:
	all_dict_out - {
	thread_summaries - {str:str}: dictionary with thread identifier as
		keys and thread summaries as values
	channel_summaries - {str:str}: dictionary with channel names as keys
		and channel summaries as values (empty dict if summarize_channel
		is false)
	server_summary - {str:str}: dictionary with "whole server" as
		single key and channel summary as value.}
	}
	token_counter - int: number of tokens used for the processing

	Notes:
	See summarize_text.py for documentation on the summarization
	"""

	# # # PREPARATIONS # # #

	# set token counter to 0
	token_counter = 0

	# initiate empty dictionary for server summary
	server_summary = {}
		
	# initiate dictionary for summaries per channel
	channel_summaries = {}

	# initiate dictionary for summaries per thread by channel
	thread_summaries = {}


	# # # SUMMARIZE # # #

	# for each dictionary key (reflecting channels)
	for chan in mess_dict_all.keys(): # select single channel only for debugging: ["backend"]: #["communityhealth"]:#

		# initiate dictionary for summaries per thread
		thread_summaries[chan] = {}
		
		# set counter to 1
		counter = 1


		# # # SUMMARIZE FOR THREADS # # #

		# for each list item index
		for thread in mess_dict_all[chan].keys():

			# if there are any messages
			if len(mess_dict_all[chan][thread].keys()) > 0:
				
				# make summary of messages and store in output dict
				thread_summaries[chan]["{}: {}".format(counter, thread)], num_tokens = \
					summarize_text(mess_dict_all[chan][thread], OA_key, True, "discord thread")
	
				# add 1 to thread counter
				counter += 1

				# add num_tokens to token counter
				token_counter += num_tokens


		# # # SUMMARIZE FOR CHANNEL # # #
		
		# if more than one thread item was summarized and a channel summary is requested
		if counter > 2 and summarize_channel:

			# make summary of all summaries
			channel_summaries[chan], num_tokens = summarize_text(thread_summaries[chan], OA_key, False, "selection of discord thread summaries")

			# add num_tokens to token counter
			token_counter += num_tokens
			
		# if only a single thread item was summarized and a channel summary is requested
		elif counter == 2 and summarize_channel:

			# store single summarized thread as channel summary
			channel_summaries[chan] = list(thread_summaries[chan].values())[0]


	# # # SUMMARIZE FOR SERVER # # #
		
	# if more than one channel was summarized and a channel and server summary are requested
	if len(channel_summaries.keys()) > 1 and summarize_channel and summarize_server:
		
		# obtain summary for server
		server_summary["whole server"], num_tokens = summarize_text(channel_summaries, OA_key, False,
																	"selection of discord channel summaries")

		# add num_tokens to token counter
		token_counter += num_tokens

	# if one channel was summarized and a channel and server summary are requested
	elif len(channel_summaries.keys()) == 1 and summarize_channel and summarize_server:		

		# store single summarized channel as server summary
		server_summary["whole server"] = list(channel_summaries.values())[0]


	# return summary dictionaries
	return {"thread_summaries": thread_summaries, "channel_summaries": channel_summaries, "server_summary": server_summary}, token_counter




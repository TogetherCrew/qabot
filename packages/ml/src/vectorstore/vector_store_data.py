# import the necessary libraries
import openai
import sys
import json
import pickle
from langchain.embeddings import OpenAIEmbeddings
from langchain.vectorstores import DeepLake
from langchain.schema import Document
from langchain.embeddings import HuggingFaceEmbeddings

import DB_interactions
from summarize_discord import summarize_discord_main


def main(args):

    # # SET PARAMETERS

    # set openai key
    OA_KEY = ""

    # set db information
    DB_CONNECTION_STR = ""
    DB_GUILD = ""
    CHANNELS_ID = [""]
    DATES = ['2023-04-13', '2023-04-14', '2023-04-15', '2023-04-16', '2023-04-17', '2023-04-18', '2023-04-19']

    # set paths to store results
    RAW_DB_SAVE_PATH = "DeepLake_VectorStore_413_419_raw_messages_HF_v2"
    SUM_DB_SAVE_PATH = "DeepLake_VectorStore_413_419_summaries_HF_v2"
    METADATA_OPTIONS_SAVE_PATH = "metadata_options.json"


    # # initiate embeddings model

    # # OpenAI embedding model
    # embeddings = OpenAIEmbeddings(openai_api_key=OA_KEY)

    # HuggingFace embeddings model
    model_name = "sentence-transformers/all-mpnet-base-v2"
    embeddings = HuggingFaceEmbeddings(model_name=model_name)

    # embed and store data
    vector_store_discord(OA_KEY, DB_CONNECTION_STR, DB_GUILD, CHANNELS_ID, DATES, embeddings,
                         RAW_DB_SAVE_PATH, SUM_DB_SAVE_PATH, METADATA_OPTIONS_SAVE_PATH)

    return

# # #

def vector_store_discord(OA_KEY, DB_CONNECTION_STR, DB_GUILD, CHANNELS_ID, DATES, embeddings,
                         RAW_DB_SAVE_PATH, SUM_DB_SAVE_PATH, METADATA_OPTIONS_SAVE_PATH):

    # set up database access
    db_access = DB_interactions.DB_access(DB_GUILD, DB_CONNECTION_STR)
    query = DB_interactions.Query()

    # obtain relations between channel id and name
    cursor = db_access.query_db_find(
        table="channels",
        feature_projection={"__v": 0, "_id": 0, "last_update": 0},
        query={"channelId": {"$in": list(CHANNELS_ID)}}
    )

    # store relations between channel id and name as dictionary
    channel_id_name = DB_interactions.filter_channel_name_id(list(cursor))

    # initiate empty doc arrays
    summary_docs = []
    raw_docs = []

    # initiate empty metadata arrays
    all_channels = []
    all_threads = []
    all_authors = []

    # for each date
    for date in DATES:

        ########## And now querying the table with messages in it ##########
        query_dict = query.create_query_threads(
            channels_id=CHANNELS_ID,
            dates=[date],
            channelsId_key='channelId',
            date_key='datetime'
        )

        projection = {
            'user_mentions': 0,
            'role_mentions': 0,
            'reactions': 0,
            'replied_user': 0,
            'type': 0,
            'messageId': 0,
            '__v': 0
        }

        cursor = db_access.query_db_find(table='rawinfos',
                                         query=query_dict,
                                         feature_projection=projection,
                                         sorting=('datetime', 1)
                                         )

        # getting a result as `thread_results : {str:{str:{str:str}}}`
        thread_results = DB_interactions.filter_channel_thread(cursor_list=list(cursor),
                                               channels_id=CHANNELS_ID,
                                               thread_id_key='thread',
                                               author_key='author',
                                               message_content_key='content')

        # run the summarizing function
        summary_out, num_tokens = summarize_discord_main(thread_results, OA_KEY, True, True)

        # add server summary to docs
        summary_docs.append(Document(page_content=summary_out['server_summary']["whole server"],
         metadata={
             'date' : date,
             'channel' : None,
             'thread' : None
         }))

        # for each channel
        for channel in summary_out['channel_summaries'].keys():

            # store channel summary data
            summary_docs.append(Document(page_content=summary_out['channel_summaries'][channel],
                                         metadata={
                                             'date': date,
                                             'channel': channel_id_name[channel],
                                             'thread': None
                                         }))

            # add channel name to metadata array if it's not in there yet
            if not channel_id_name[channel] in all_channels:
                all_channels.append(channel_id_name[channel])

            # for each thread
            for thread_label in summary_out['thread_summaries'][channel].keys():

                # split thread name
                thread_name_split = thread_label.split(": ")
                thread = thread_name_split[1]

                # store thread summary data
                summary_docs.append(Document(page_content=summary_out['thread_summaries'][channel][thread_label],
                                             metadata={
                                                 'date': date,
                                                 'channel': channel_id_name[channel],
                                                 'thread': thread
                                             }))

                # add thread name to metadata array if it's not in there yet
                if not thread in all_threads:
                    all_threads.append(thread)

                # for each message
                for mess in thread_results[channel][thread].keys():

                    # split message id
                    mess_id_split = mess.split(":")

                    # split author name from handle
                    handle_split = mess_id_split[1].split("#")

                    # if message contains text
                    if len(thread_results[channel][thread][mess]) > 1:

                        # store message
                        raw_docs.append(Document(page_content=thread_results[channel][thread][mess],
                                                     metadata={
                                                         'date': date,
                                                         'channel': channel_id_name[channel],
                                                         'thread': thread,
                                                         'author' : handle_split[0],
                                                         'index' : mess_id_split[0]
                                                     }))

                        # add author name to metadata array if it's not in there yet
                        if not handle_split[0] in all_authors:
                            all_authors.append(handle_split[0])


    # store results in vector stores
    db_raw = DeepLake.from_documents(raw_docs, embeddings, dataset_path=RAW_DB_SAVE_PATH)
    db_summary = DeepLake.from_documents(summary_docs, embeddings, dataset_path=SUM_DB_SAVE_PATH)

    # store metadata options for vector stores
    JSON_dict = {"all_channels":all_channels, "all_threads":all_threads, "all_authors":all_authors, "all_dates":DATES}

    with open(METADATA_OPTIONS_SAVE_PATH, "w") as outfile:
        json.dump(JSON_dict, outfile)

    return

if __name__ == '__main__':
    sys.exit(main(sys.argv))
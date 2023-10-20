from numpy import zeros, squeeze
from pymongo import MongoClient
from datetime import datetime

class DB_access:

   def __init__(self, db_name, connection_string) -> None:
      self.db_client = self._get_database(db_name, connection_string)

   def _get_database(self, db_name, connection_string):
      """
      get the database instance
      Parameters:
      ------------
      db_name : string
         the name of the database to use
      connection_string : string
         the url of connection
      Returns:
      ---------
      client : MongoClient
         the mongodb client to access
      """
      client = MongoClient(connection_string)
      return client[db_name]

   def _db_call(self, calling_function, query, feature_projection=None, sorting=None):
      """
      call the function on database, it could be whether aggragation or find
      Parameters:
      -------------
      calling_function : function
         can be `MongoClient.find` or `MongoClient.aggregate`
      query : dictionary
         the query as a dictionary
      feature_projection : dictionary
         the dictionary to or not to project the results on it
         default is None, meaning to return all features
      sorting : tuple
         sort the results base on the input dictionary
         if None, then do not sort the results
      Returns:
      ----------
      cursor : mongodb Cursor
         cursor to get the information of a query
      """
      ## if there was no projection available
      if feature_projection is None:
         ## if sorting was given
         if sorting is not None:
            cursor = calling_function(query).sort(sorting[0], sorting[1])
         else:
            cursor = calling_function(query)
      else:
         if sorting is not None:
            cursor = calling_function(query, feature_projection).sort(sorting[0], sorting[1])
         else:
            cursor = calling_function(query, feature_projection)

      return cursor

   def query_db_aggregation(self, query, table, feature_projection=None, sorting=None):
      """
      aggregate the database using query
      Parameters:
      ------------
      table : string
         the table name to retrieve the data
      query : dictionary
         the query as a dictionary
      feature_projection : dictionary
         the dictionary to or not to project the results on it
         default is None, meaning to return all features
      Returns:
      ----------
      cursor : mongodb Cursor
         cursor to get the information of a query
      """

      cursor = self._db_call(calling_function=self.db_client[table].aggregate,
                             query=query,
                             feature_projection=feature_projection,
                             sorting=sorting)

      return cursor

   def query_db_find(self, table, query, feature_projection=None, sorting=None):
      """
      aggregate the database using query
      Parameters:
      ------------
      table : string
         the table name to retrieve the data
      query : dictionary
         the query as a dictionary
      feature_projection : dictionary
         the dictionary to or not to project the results on it
         default is None, meaning to return all features
      Returns:
      ----------
      cursor : mongodb Cursor
         cursor to get the information of a query
      """
      cursor = self._db_call(calling_function=self.db_client[table].find,
                             query=query,
                             feature_projection=feature_projection,
                             sorting=sorting)
      return cursor


class Query():

    def __init__(self) -> None:
        """
        create different queries to query the database
        """
        pass

    def _check_inputs(self, acc_names, channels, dates, variable_aggregation_type='and', value_aggregation_type='or'):
        """
        just check whether the inputs are correctly entered or not
        """
        #### checking the length of arrays ####
        if len(acc_names) < 1:
            raise ValueError(f"acc_names array is empty!")
        if len(channels) < 1:
            raise ValueError(f"channels array is empty!")
        if len(dates) < 1:
            raise ValueError(f"dates array is empty!")

        ## checking the variable aggregation_type variable
        if variable_aggregation_type not in ['and', 'or']:
            raise ValueError(
                f'variable aggregation type must be either `and` or `or`!\nentered value is:{variable_aggregation_type}')

        ## checking the value aggregation_type variable
        if value_aggregation_type not in ['and', 'or']:
            raise ValueError(
                f'value aggregation type must be either `and` or `or`!\nentered value is:{value_aggregation_type}')

    def create_query_filter_account_channel_dates(self,
                                                  acc_names,
                                                  channels,
                                                  date_range,
                                                  variable_aggregation_type='and',
                                                  value_aggregation_type='or',
                                                  date_key='createdDate',
                                                  channel_key='channelId',
                                                  account_key='account'):
        """
        A query to filter the database on account_name, and/or channel_names, and/or dates
        the aggregation of varibales (`account_name`, `channels`, and `dates`) can be set to `and` or `or`

        Parameters:
        ------------
        acc_names : list of string
            each string is an account name that needs to be included.
            The minimum length of this list is 1
        channels : list of string
            each string is a channel identifier for the channels that need to be included.
            The minimum length of this list is 1
        date_range : tuple
            tuple of date, the first one is starting date and the second is ending date
            the format of each one is %Y-%m-%d
        variable_aggregation_type : string
            values can be [`and`, `or`], the aggregation type between the variables (variables are `acc_names`, `channels`, and `dates`)
            `or` represents the or between the queries of acc_name, channels, dates
            `and` represents the and between the queries of acc_name, channels, dates
            default value is `and`
        value_aggregation_type : string
            values can be [`and`, `or`], the aggregation type between the values of each variable
            `or` represents the `or` operation between the values of input arrays
            `and` represents the `and` operation between the values of input arrays
            default value is `or`
        date_key : string
            the name of the field of date in database
            default is `date`
        channel_key : string
            the id of the field of channel name in database
            default is `channelId`
        account_key : string
            the name of the field account name in the database
            default is `account`
        Returns:
        ----------
        query : dictionary
            the query to get access
        """

        #### creating each part of query seperately ####

        ## creating date query
        ## in datettime format
        date_range_dt = [
            datetime.strptime(date_range[0], "%Y-%m-%d"),
            datetime.strptime(date_range[1], "%Y-%m-%d")
        ]
        datetime_query = {
            date_key : {
                "$gte": date_range_dt[0],
                "$lte": date_range_dt[1]
            }
        }

        ## creating channels query
        channel_query = []

        for ch in channels:
            channel_query.append({channel_key: ch})

        ## creating the account_name query
        account_query = []

        for account in acc_names:
            account_query.append({account_key: account})

        #### creating the query ####
        query = {
            '$' + variable_aggregation_type: [
                {'$' + value_aggregation_type: account_query},
                {'$' + value_aggregation_type: channel_query},
                ## for time we should definitly use `or` because `and` would result in nothing!
                datetime_query
            ]
        }

        return query

    def create_query_channel(self, channels_name):
        """
        create a dictionary of query to get channel_id using channel_name
        Parameters:
        -------------
        channel_name : list
            a list of channel names to retrive their id

        Returns:
        ---------
        query : dictionary
            the query to retrieve the channel ids
        """
        query_channelId = {'channel': {'$in': channels_name}}

        return query_channelId

    def create_query_threads(self, channels_id, date_range, channelsId_key='channelId', date_key='createdDate') -> dict:
        """
        create a dictionary of query to query the DB, getting the messages for specific channels and dates
        Parameters:
        ------------
        channels_id : list
            list of strings, each string is a channel identifier for the channels that needs to be included.
            The minimum length of this list is 1
        date_range : tuple
            tuple of date, the first one is starting date and the second is ending date
            the format of each one is %Y-%m-%d
        channelsId_key : string
            the field name corresponding to chnnel id in database
            default value is `channelId`
        date_key : string
            the field name corresponding to date in database
            default value is `date`

        Returns:
        ---------
        query : dictionary
            a dictionary that query the database
        """
        #### Array inputs checking ####
        if len(channels_id) < 1:
            raise ValueError(f"channels_id array is empty!")
        if len(date_range) != 2:
            raise ValueError(f"dates range is given wrong!")

        datetime_query = []

        ## in datettime format
        date_range_dt = [
            datetime.strptime(date_range[0], "%Y-%m-%d"),
            datetime.strptime(date_range[1], "%Y-%m-%d")
        ]
        datetime_query = {
            date_key : {
                "$gte": date_range_dt[0],
                "$lte": date_range_dt[1]
            }
        }

        query = {
            '$and': [
                {channelsId_key: {'$in': channels_id}},
                datetime_query,
                ## do not return the messages with no thread
                {'threadId': {'$ne': None}}
            ]
        }

        return query


def sum_interactions_features(cursor_list, dict_keys):
    """
    sum the interactions per hour
    Parameters:
    ------------
    cursor_list : list
       the db cursor returned and converted as list
    dict_keys : list
       the list of dictionary keys, representing the features in database

    Returns:
    ----------
    summed_counts_per_hour : dictionary
       the dictionary of each feature having summed the counts per hour, the dictionary of features is returned
    """

    summed_counts_per_hour = {}
    for key in dict_keys:
        summed_counts_per_hour[key] = zeros(24)

    for key in dict_keys:
        ## the array of hours 0:23
        for data in cursor_list:
            summed_counts_per_hour[key] += data[key]

    return summed_counts_per_hour


def per_account_interactions(cursor_list,
                             dict_keys=['replier_accounts', 'reacter_accounts', 'mentioner_accounts'],
                             ):
    """
    get per account interactions as `mentioner_accounts`, `reacter_accounts`, and `replier_accounts` (summing)
    Parameters:
    ------------
    cursor_list : list
        the db cursor returned and converted as list
    dict_keys : list
        the list of dictionary keys, representing the features in database
    Returns:
    ----------
    summed_per_account_interactions : dictionary
        the dictionary of each feature having summed the counts per hour, the dictionary of features is returned
    """

    per_acc_interactions = {}

    ## initialze the fields of the dictionary
    for feature in dict_keys:
        per_acc_interactions[feature] = {}

    ## for each feature
    for feature in dict_keys:
        ## for each record retrieved from DB
        for db_records in cursor_list:
            ## for each interactor type in record
            for db_interactor in db_records[feature]:

                ## because of DB inconsistency
                ## there was a list of one item always in one of the servers
                ## so we're getting the first or the one item available of it
                if type(db_interactor) is list:
                    db_interactor_ = db_interactor[0]
                ## else, if the inconsistency wasn't available
                else:
                    db_interactor_ = db_interactor

                acc_name = db_interactor_['account']
                ## if the account wasn't available in saved dictionary
                ## then simply set the counts to the saved dictionary
                if acc_name not in per_acc_interactions[feature].keys():
                    per_acc_interactions[feature][acc_name] = db_interactor_['count']
                ## else, sum the count to it
                else:
                    per_acc_interactions[feature][acc_name] += db_interactor_['count']

    ## remaking the dictionaries into the format of database

    per_acc_interactions_db_style = {}
    all_interactions_per_acc = {}

    ## for the interaction type, e.g.: `replier_accounts`
    for key in per_acc_interactions.keys():
        per_acc_interactions_db_style[key] = {}

        ## for each account which is saved as a key
        for idx, acc_name in enumerate(per_acc_interactions[key].keys()):

            interaction_count = per_acc_interactions[key][acc_name]
            per_acc_interactions_db_style[key][idx] = {
                'account': acc_name,
                'count': interaction_count}

            ## if the account was available in the dictionary of all interactions
            if acc_name in all_interactions_per_acc.keys():
                all_interactions_per_acc[acc_name] += interaction_count
            ## else it wasn't available, then create the account with its interaction count
            else:
                all_interactions_per_acc[acc_name] = interaction_count

    per_acc_interactions_db_style['all_interaction_accounts'] = {}

    ## adding the all interactions_per_acc to one dictionary
    for idx, acc_name in enumerate(all_interactions_per_acc.keys()):
        per_acc_interactions_db_style['all_interaction_accounts'][str(idx)] = {
            'account': acc_name,
            'count': all_interactions_per_acc[acc_name]
        }

    summed_per_account_interactions = per_acc_interactions_db_style

    return summed_per_account_interactions


def filter_channel_name_id(cursor_list,
                           channel_name_key='channel',
                           channel_id_key='channelId'):
    """
    filter the cursor list retrieved from DB for channels and their ids

    Parameters:
    -------------
    cursor_list : list of dictionaries
        the retreived values of DB
    channel_name_key : string
        the name of channel_name field in DB
        default is `channel`
    channel_id_key : string
        the name of channel_id field in DB
        default is `channelId`
    Returns:
    ----------
    channels_id_dict : dictionary
        a dictionary with keys as channel_id and values as channel_name
    """
    channels_id_dict = {}
    for ch_id_dict in cursor_list:
        ## the keys in dict are channel id
        chId = ch_id_dict[channel_id_key]
        ## and the values of dict are the channel name
        channels_id_dict[chId] = ch_id_dict[channel_name_key]

    return channels_id_dict


def filter_channel_thread(cursor_list,
                          channels_id,
                          thread_id_key='threadId',
                          author_key='author',
                          message_content_key='content'):
    """
    create a dictionary of channels and threads for messages, sorted by time descending
    Parameters:
    ------------
    cursor_list : list of dictionaries
        the list of values in DB containing a thread and messages of authors
    channels_id : list
        a list of channels id
        minimum length of the list is 1
    thread_id_key : string
        the name of the thread id field in DB
    author_key : string
        the name of the author field in DB
    message_content_key : string
        the name of the message content field in DB

    Returns:
    ----------
    channel_thread_dict : {str:{str:{str:str}}}
        a dictionary having keys of channel names, and per thread messages as dictionary
    # An example of output can be like this:
    {
        “CHANNEL_ID1” :
        {
            “THREAD_ID1” :
            {
                “1:@user1”: “Example message 1”,
                “2:@user2”: “Example message 2”,
                …
            },
            “THREAD_ID2” :
                {More example messages in same format}, …},
        “CHANNEL_ID2” :
            {More thread dictionaries with example messages in same format}, …},
        More channel dictionaries with thread dictionaries with example messages in same format,
            …
    }
    """
    ######### First we're filtering the records via their channel name #########
    channels_dict = {}
    ## create an empty array of each channel
    for ch_id in channels_id:
        channels_dict[ch_id] = []

    ## filtering through the channel name field in dictionary
    for record in cursor_list:
        chId = record['channelId']
        channels_dict[chId].append(record)

    ######### and the adding the filtering of thread id #########
    channel_thread_dict = {}

    ## filtering threads
    for chId in channels_dict.keys():
        channel_thread_dict[chId] = {}
        ## initialize the index
        idx = 1
        for record in channels_dict[chId]:
            ## get the record id, its exactly the thread id
            threadId = record[thread_id_key]
            ## we could instead of threadId use thread names
            ## for that the `thread` should be used here instead of `thread_id_key` in above code

            ## if the thread wasn't available in dict
            ## then make a dictionary for that
            if threadId not in channel_thread_dict[chId].keys():
                ## reset the idx for each thread
                idx = 1
                ## creating the first message
                channel_thread_dict[chId][threadId] = {f'{idx}:{record[author_key]}': record[message_content_key]}

            ## if the thread was created before
            ## then add the author content data to the dictionary
            else:
                ## increase the index for the next messages in thread
                idx += 1
                channel_thread_dict[chId][threadId][f'{idx}:{record[author_key]}'] = record[message_content_key]

    return channel_thread_dict



# from numpy import zeros, squeeze
#
#
# class Query():
#
#     def __init__(self) -> None:
#         """
#         create different queries to query the database
#         """
#         pass
#
#
#
#     def _check_inputs(self, acc_names, channels, dates, variable_aggregation_type='and', value_aggregation_type='or'):
#         """
#         just check whether the inputs are correctly entered or not
#         """
#         #### checking the length of arrays ####
#         if len(acc_names) < 1:
#             raise ValueError(f"acc_names array is empty!")
#         if len(channels) < 1:
#             raise ValueError(f"channels array is empty!")
#         if len(dates) < 1:
#             raise ValueError(f"dates array is empty!")
#
#         ## checking the variable aggregation_type variable
#         if variable_aggregation_type not in ['and', 'or']:
#             raise ValueError(f'variable aggregation type must be either `and` or `or`!\nentered value is:{variable_aggregation_type}')
#
#         ## checking the value aggregation_type variable
#         if value_aggregation_type not in ['and', 'or']:
#             raise ValueError(f'value aggregation type must be either `and` or `or`!\nentered value is:{value_aggregation_type}')
#
#     def create_query_filter_account_channel_dates(self,
#                                                   acc_names,
#                                                   channels,
#                                                   dates,
#                                                   variable_aggregation_type='and',
#                                                   value_aggregation_type='or',
#                                                   date_key='date',
#                                                   channel_key='channelId',
#                                                   account_key = 'account'):
#         """
#         A query to filter the database on account_name, and/or channel_names, and/or dates
#         the aggregation of varibales (`account_name`, `channels`, and `dates`) can be set to `and` or `or`
#
#
#         Parameters:
#         ------------
#         acc_names : list of string
#             each string is an account name that needs to be included.
#             The minimum length of this list is 1
#         channels : list of string
#             each string is a channel identifier for the channels that need to be included.
#             The minimum length of this list is 1
#         dates : list of datetime
#             each datetime object is a date that needs to be included.
#             The minimum length of this list is 1
#             should be in type of `%Y-%m-%d` which is the exact database format
#         variable_aggregation_type : string
#             values can be [`and`, `or`], the aggregation type between the variables (variables are `acc_names`, `channels`, and `dates`)
#             `or` represents the or between the queries of acc_name, channels, dates
#             `and` represents the and between the queries of acc_name, channels, dates
#             default value is `and`
#         value_aggregation_type : string
#             values can be [`and`, `or`], the aggregation type between the values of each variable
#             `or` represents the `or` operation between the values of input arrays
#             `and` represents the `and` operation between the values of input arrays
#             default value is `or`
#         date_key : string
#             the name of the field of date in database
#             default is `date`
#         channel_key : string
#             the id of the field of channel name in database
#             default is `channelId`
#         account_key : string
#             the name of the field account name in the database
#             default is `account`
#
#         Returns:
#         ----------
#         query : dictionary
#             the query to get access
#         """
#
#         #### creating each part of query seperately ####
#
#         ## creating date query
#         date_query = []
#         for date in dates:
#             date_query.append({date_key: {'$regex': date}})
#
#         ## creating channels query
#         channel_query = []
#
#         for ch in channels:
#             channel_query.append({channel_key: ch})
#
#         ## creating the account_name query
#         account_query = []
#
#         for account in acc_names:
#             account_query.append({account_key: account})
#
#         #### creating the query ####
#         query = {
#             '$' + variable_aggregation_type: [
#                 {'$' + value_aggregation_type: account_query},
#                 {'$' + value_aggregation_type: channel_query},
#                 ## for time we should definitly use `or` because `and` would result in nothing!
#                 {'$or': date_query}
#             ]
#         }
#
#         return query
#
#
#     def create_query_threads(self, channels_id, dates, channelsId_key='channelId', date_key='date') -> dict:
#         """
#         create a dictionary of query to query the DB, getting the messages for specific channels and dates
#         Parameters:
#         ------------
#         channels_id : list
#             list of strings, each string is a channel identifier for the channels that needs to be included.
#             The minimum length of this list is 1
#         dates : list
#             list of datetime objects, each datetime object is a date that needs to be included.
#             The minimum length of this list is 1
#         channelsId_key : string
#             the field name corresponding to chnnel id in database
#             default value is `channelId`
#         date_key : string
#             the field name corresponding to date in database
#             default value is `date`
#
#         Returns:
#         ---------
#         query : dictionary
#             a dictionary that query the database
#         """
#         #### Array inputs checking ####
#         if len(channels_id) < 1:
#             raise ValueError(f"channels_id array is empty!")
#         if len(dates) < 1:
#             raise ValueError(f"dates array is empty!")
#
#         datetime_query = []
#         for date in dates:
#             datetime_query.append({date_key: {'$regex': date}})
#
#         query = {
#             '$and': [
#                 {channelsId_key: {'$in': channels_id}},
#                 {'$or': datetime_query},
#                 ## do not return the messages with no thread
#                 {'thread': {'$ne': 'None'}}
#             ]
#         }
#
#         return query
#
#
# def sum_interactions_features(cursor_list, dict_keys):
#    """
#    sum the interactions per hour
#
#    Parameters:
#    ------------
#    cursor_list : list
#       the db cursor returned and converted as list
#    dict_keys : list
#       the list of dictionary keys, representing the features in database
#
#    Returns:
#    ----------
#    summed_counts_per_hour : dictionary
#       the dictionary of each feature having summed the counts per hour, the dictionary of features is returned
#    """
#
#    summed_counts_per_hour = {}
#    for key in dict_keys:
#       summed_counts_per_hour[key] = zeros(24)
#
#    for key in dict_keys:
#       ## the array of hours 0:23
#       for data in cursor_list:
#          summed_counts_per_hour[key] += data[key]
#
#    return summed_counts_per_hour
#
#
# def per_account_interactions(cursor_list,
#                              dict_keys=['replier_accounts', 'reacter_accounts', 'mentioner_accounts'],
#                              ):
#     """
#     get per account interactions as `mentioner_accounts`, `reacter_accounts`, and `replier_accounts` (summing)
#
#     Parameters:
#     ------------
#     cursor_list : list
#         the db cursor returned and converted as list
#     dict_keys : list
#         the list of dictionary keys, representing the features in database
#
#     Returns:
#     ----------
#     summed_per_account_interactions : dictionary
#         the dictionary of each feature having summed the counts per hour, the dictionary of features is returned
#     """
#
#     per_acc_interactions = {}
#
#     ## initialze the fields of the dictionary
#     for feature in dict_keys:
#         per_acc_interactions[feature] = {}
#
#     ## for each feature
#     for feature in dict_keys:
#         ## for each record retrieved from DB
#         for db_records in cursor_list:
#             ## for each interactor type in record
#             for db_interactor in db_records[feature]:
#
#                 ## because of DB inconsistency
#                 ## there was a list of one item always in one of the servers
#                 ## so we're getting the first or the one item available of it
#                 if type(db_interactor) is list:
#                     db_interactor_ = db_interactor[0]
#                 ## else, if the inconsistency wasn't available
#                 else:
#                     db_interactor_ = db_interactor
#
#                 acc_name = db_interactor_['account']
#                 ## if the account wasn't available in saved dictionary
#                 ## then simply set the counts to the saved dictionary
#                 if acc_name not in per_acc_interactions[feature].keys():
#                     per_acc_interactions[feature][acc_name] = db_interactor_['count']
#                 ## else, sum the count to it
#                 else:
#                     per_acc_interactions[feature][acc_name] += db_interactor_['count']
#
#     ## remaking the dictionaries into the format of database
#
#     per_acc_interactions_db_style = {}
#     all_interactions_per_acc = {}
#
#
#     ## for the interaction type, e.g.: `replier_accounts`
#     for key in per_acc_interactions.keys():
#         per_acc_interactions_db_style[key] = {}
#
#         ## for each account which is saved as a key
#         for idx, acc_name in enumerate(per_acc_interactions[key].keys()):
#
#             interaction_count = per_acc_interactions[key][acc_name]
#             per_acc_interactions_db_style[key][idx] = {
#                 'account': acc_name,
#                 'count': interaction_count}
#
#
#
#             ## if the account was available in the dictionary of all interactions
#             if acc_name in all_interactions_per_acc.keys():
#                 all_interactions_per_acc[acc_name] += interaction_count
#             ## else it wasn't available, then create the account with its interaction count
#             else:
#                 all_interactions_per_acc[acc_name] = interaction_count
#
#
#     per_acc_interactions_db_style['all_interaction_accounts'] = {}
#
#     ## adding the all interactions_per_acc to one dictionary
#     for idx, acc_name in enumerate(all_interactions_per_acc.keys()):
#         per_acc_interactions_db_style['all_interaction_accounts'][str(idx)] = {
#             'account': acc_name,
#             'count': all_interactions_per_acc[acc_name]
#         }
#
#     summed_per_account_interactions = per_acc_interactions_db_style
#
#     return summed_per_account_interactions
#
#
# def filter_channel_name_id(cursor_list,
#                            channel_name_key='channel',
#                            channel_id_key='channelId'):
#     """
#     filter the cursor list retrieved from DB for channels and their ids
#
#     Parameters:
#     -------------
#     cursor_list : list of dictionaries
#         the retreived values of DB
#     channel_name_key : string
#         the name of channel_name field in DB
#         default is `channel`
#     channel_id_key : string
#         the name of channel_id field in DB
#         default is `channelId`
#     Returns:
#     ----------
#     channels_id_dict : dictionary
#         a dictionary with keys as channel_id and values as channel_name
#     """
#     channels_id_dict = {}
#     for ch_id_dict in cursor_list:
#         ## the keys in dict are channel id
#         chId = ch_id_dict[channel_id_key]
#         ## and the values of dict are the channel name
#         channels_id_dict[chId] = ch_id_dict[channel_name_key]
#
#     return channels_id_dict
#
#
# def filter_channel_thread(cursor_list,
#                           channels_id,
#                           thread_id_key='threadId',
#                           author_key='author',
#                           message_content_key='content'):
#     """
#     create a dictionary of channels and threads for messages, sorted by time descending
#     Parameters:
#     ------------
#     cursor_list : list of dictionaries
#         the list of values in DB containing a thread and messages of authors
#     channels_id : list
#         a list of channels id
#         minimum length of the list is 1
#     thread_id_key : string
#         the name of the thread id field in DB
#     author_key : string
#         the name of the author field in DB
#     message_content_key : string
#         the name of the message content field in DB
#
#     Returns:
#     ----------
#     channel_thread_dict : {str:{str:{str:str}}}
#         a dictionary having keys of channel names, and per thread messages as dictionary
#     # An example of output can be like this:
#     {
#         “CHANNEL_ID1” :
#         {
#             “THREAD_ID1” :
#             {
#                 “1:@user1”: “Example message 1”,
#                 “2:@user2”: “Example message 2”,
#                 …
#             },
#             “THREAD_ID2” :
#                 {More example messages in same format}, …},
#         “CHANNEL_ID2” :
#             {More thread dictionaries with example messages in same format}, …},
#         More channel dictionaries with thread dictionaries with example messages in same format,
#             …
#     }
#     """
#     ######### First we're filtering the records via their channel name #########
#     channels_dict = {}
#     ## create an empty array of each channel
#     for ch_id in channels_id:
#         channels_dict[ch_id] = []
#
#     ## filtering through the channel name field in dictionary
#     for record in cursor_list:
#         chId = record['channelId']
#         channels_dict[chId].append(record)
#
#     ######### and the adding the filtering of thread id #########
#     channel_thread_dict = {}
#
#     ## filtering threads
#     for chId in channels_dict.keys():
#         channel_thread_dict[chId] = {}
#         ## initialize the index
#         idx = 1
#         for record in channels_dict[chId]:
#             ## get the record id, its exactly the thread id
#             threadId = record[thread_id_key]
#             ## we could instead of threadId use thread names
#             ## for that the `thread` should be used here instead of `thread_id_key` in above code
#
#             ## if the thread wasn't available in dict
#             ## then make a dictionary for that
#             if threadId not in channel_thread_dict[chId].keys():
#                 ## reset the idx for each thread
#                 idx = 1
#                 ## creating the first message
#                 channel_thread_dict[chId][threadId] = {f'{idx}:{record[author_key]}': record[message_content_key]}
#
#             ## if the thread was created before
#             ## then add the author content data to the dictionary
#             else:
#                 ## increase the index for the next messages in thread
#                 idx += 1
#                 channel_thread_dict[chId][threadId][f'{idx}:{record[author_key]}'] = record[message_content_key]
#
#     return channel_thread_dict
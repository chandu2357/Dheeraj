import os
import argparse
import logging
import json
import datetime
import subprocess
from pathlib import Path
from os import path, makedirs

# All the key nodes of json file are constants.
# Example: "mobile_response", "views", "type", "data", "references"
# The values nodes of json may differ:
# Example 1: "symbols": "LGFB" should be string and contain any number of strings. But everything should be string
# Exmaple 2: under "data", "symbol": "value" should be string; "price": "15.43" should be decimal; "timeString": "November 5, 2021, 03:10 PM EST", should be this format
# Exmaple 3: "timeString2": "11/5/2021, 04:10 PM ET" should be this format and "percentChange": "+26.47%" should be either + or - decimal percentage

def verify_string(data):



def verify_symbol_existence_in_the_list(data):


def check_data_references_values(data):
    # Values to check for keys
    # "symbol", "productType", "exchangeCode", "exchangeName", "exchangeDesc", "typeName", "typeDesc", "symbolDescription";
    # "low", "fastMktFlag", "asksize", "price", "bid", "bidsize", "quoteType", "quoteStatus", "newsFlag", "close", "high", "timeZone";
    # "ask", "volume", "open", "quoteExchangeCode", "quoteSymbol", "timeStamp", "haltedFlag", "change", "timeString", "timeString2", "percentChange"

###verify symbol
    if "symbol" in data:
        if type(data["symbol"]) != str:
            print("Data Reference Value Error. The value pair of the key 'symbol' is not a string")
###verify productType
    if "productType" in data:
        if type(data["productType"]) != str:
            print("Data Reference Value Error. The value pair of the key 'productType' is not a string")
###verify exchangeCode
    if "exchangeCode" in data:
        if type(data["exchangeCode"]) != str:
            print("Data Reference Value Error. The value pair of the key 'exchangeCode' is not a string")
###verify exchangeName
    if "exchangeName" in data:
        if type(data["exchangeName"]) != str:
            print("Data Reference Value Error. The value pair of the key 'exchangeName' is not a string")
###verify exchangeDesc
    if "exchangeDesc" in data:
        ö
    if "typeName" in data:
        if type(data["typeName"]) != str:
            print("Data Reference Value Error. The value pair of the key 'typeName' is not a string")
###verify typeDesc
    if "typeDesc" in data:
        if type(data["typeDesc"]) != str:
            print("Data Reference Value Error. The value pair of the key 'typeDesc' is not a string")
###verify symbolDescription
    if "symbolDescription" in data:
        if type(data["symbolDescription"]) != str:
            print("Data Reference Value Error. The value pair of the key 'symbolDescription' is not a string")
###verify low
    if "low" in data:
        if data["low"].isdecimal() == True:
                print("Data Reference Value Error. The value pair of the key 'low' is not a float" + data["low"])
        try:
            float(data["low"])
        except:
            print("Data Reference Value Error. The value pair of the key 'low' is not a float" + data["low"])
###verify fastMktFlag
    if "fastMktFlag" in data:
        if type(data["fastMktFlag"]) != int:
                print("Data Reference Value Error. The value pair of the key 'fastMktFlag' is not a integer")
###verify asksize
    if "asksize" in data:
        if type(data["asksize"]) != int:
                print("Data Reference Value Error. The value pair of the key 'asksize' is not a integer")
###verify price
    if "price" in data:
        if data["price"].isdecimal() == True:
            print("Data Reference Value Error. The value pair of the key 'price' is not a float" + data["price"])
        try:
            float(data["price"])
        except:
            print("Data Reference Value Error. The value pair of the key 'price' is not a float" + data["price"])
###verify bid
    if "bid" in data:
        if data["bid"].isdecimal() == True:
            print("Data Reference Value Error. The value pair of the key 'bid' is not a float" + "It is: " + data["bid"])
        try:
            float(data["bid"])
        except:
            print("Data Reference Value Error. The value pair of the key 'bid' is not a float" + "It is: " + data["bid"])
###verify bidsize
    if "bidsize" in data:
        if type(data["bidsize"]) != int:
                print("Data Reference Value Error. The value pair of the key 'bidsize' is not a integer" + "It is: " + data["bidsize"])
###verify quoteType
    if "quoteType" in data:
        if type(data["quoteType"]) != str:
            print("Data Reference Value Error. The value pair of the key 'quoteType' is not a string" + "It is: " + data["quoteType"])
###verify quoteStatus
    if "quoteStatus" in data:
        if type(data["quoteStatus"]) != int:
            print("Data Reference Value Error. The value pair of the key 'quoteStatus' is not a integer" + "It is: " + data["quoteType"])
###verify newsFlag
    if "newsFlag" in data:
        if type(data["newsFlag"]) != bool:
            print("Data Reference Value Error. The value pair of the key 'newsFlag' is not a boolean" + "It is: " + data["newsFlag"])
###verify close
    if "close" in data:
        if data["close"].isdecimal() == True:
            print("Data Reference Value Error. The value pair of the key 'close' is not a float" + "It is: " + data["close"])
        try:
            float(data["close"])
        except:
            print("Data Reference Value Error. The value pair of the key 'close' is not a float" + "It is: " + data["close"])
###verify high
    if "high" in data:
        if data["high"].isdecimal() == True:
            print("Data Reference Value Error. The value pair of the key 'high' is not a float" + "It is: " + data["high"])
        try:
            float(data["high"])
        except:
            print("Data Reference Value Error. The value pair of the key 'high' is not a float" + "It is: " + data["high"])
###verify timeZone
    if "timeZone" in data:
        if data["timeZone"] != "EST":
            print("Data Reference Value Error. The value pair of the key 'timeZone' is not a EST" + "It is: " + data["timeZone"])
###verify ask
    if "ask" in data:
        if data["ask"].isdecimal() == True:
            print("Data Reference Value Error. The value pair of the key 'ask' is not a float" + "It is: " + data["ask"])
        try:
            float(data["ask"])
        except:
            print("Data Reference Value Error. The value pair of the key 'ask' is not a float" + "It is: " + data["ask"])
###verify volume
    if "volume" in data:
        val = data["volume"].split(",")
        for item in val:
            if item.isdigit() != True:
                print("Data Reference Value Error. The value pair of the key 'volume' is not a digit" + "It is: " + data["volume"])
###verify open
    if "open" in data:
        if data["open"].isdecimal() == True:
            print("Data Reference Value Error. The value pair of the key 'open' is not a float" + "It is: " + data["open"])
        try:
            float(data["open"])
        except:
            print("Data Reference Value Error. The value pair of the key 'open' is not a float" + "It is: " + data["open"])
###verify quoteExchangeCode
    if "quoteExchangeCode" in data:
        if type(data["quoteExchangeCode"]) != str:
            print("Data Reference Value Error. The value pair of the key 'quoteExchangeCode' is not a string" + "It is: " + data["quoteExchangeCode"])
###verify quoteSymbol
    if "quoteSymbol" in data:
        if type(data["quoteSymbol"]) != str:
            print("Data Reference Value Error. The value pair of the key 'quoteSymbol' is not a string" + "It is: " + data["quoteSymbol"])
###verify timeStamp
    if "timeStamp" in data:
        val = data["timeStamp"][0:-7]
        try:
            datetime.datetime.strptime(val, "%B %d, %Y, %H:%M")
        except:
            print("Data Reference Value Error. The value pair of the key 'timeStamp' is not in proper format" + "It is: " + data["timeStamp"])
###haltedFlag
    if "haltedFlag" in data:
        if type(data["haltedFlag"]) != int:
            print("Data Reference Value Error. The value pair of the key 'haltedFlag' is not a integer" + "It is: " + data["haltedFlag"])
###verify change
    if "change" in data:
        #if data["change"].startswith("+") or data["change"].startswith("-"):
            #print("True")
        if (data["change"][0] != "+") and (data["change"][0] != "-"):
            print("Data Reference Value Error. The value pair of the key 'change' first value is not +/- a modulous float.. " + "It is: " + data["change"])
        if data["change"][1:].isdecimal() == True:
            print("Data Reference Value Error. The value pair of the key 'change' is not a modulous float" + "It is: " + data["change"])
        try:
            float(data["change"][1:])
        except:
            print("Data Reference Value Error. The value pair of the key 'change' is not a modulous float" + "It is: " + data["change"])
###verify timeString
    if "timeString" in data:
        val = data["timeString"][0:-7]
        try:
            datetime.datetime.strptime(val, "%B %d, %Y, %H:%M")
        except:
            print("Data Reference Value Error. The value pair of the key 'timeString' is not in proper format" + "It is: " + data["timeString"])
###verify timeString2
    if "timeString2" in data:
        val = data["timeString2"][0:-6]
        try:
            datetime.datetime.strptime(val, "%d/%m/%Y, %H:%M")
        except:
            print("Data Reference Value Error. The value pair of the key 'timeString2' is not in proper format" + "It is: " + data["timeString2"])
###verify percentChange
    if "percentChange" in data:
        if (data["percentChange"][0] != "+") and (data["percentChange"][0] != "-"):
            print("Data Reference Value Error. The value pair of the key 'percentChange' is not a modulous float percentage" + "It is: " + data["percentChange"])
        if data["percentChange"][-1] != "%":
            print("No '%'. Data Reference Value Error. The value pair of the key 'percentChange' is not a modulous float percentage" + "It is: " + data["percentChange"])
        if data["percentChange"][1:-1].isdecimal() == True:
            print("Data Reference Value Error. The value pair of the key 'percentChange' is not a modulous float percentage" + "It is: " + data["percentChange"])
        try:
            float(data["percentChange"][1:-1])
        except:
            print("Data Reference Value Error. The value pair of the key 'percentChange' is not a modulous float percentage" + "It is: " + data["percentChange"])



def json_automate(out_file_path):
    # Json parsing and comparison
    with open(out_file_path + "/dollar_top_gain.json") as f:
        hil_flow_control_packets = json.load(f)

    # now verify the flow control values:
    #mobile_reponse_type = hil_flow_control_packets['mobile_response']['views']['type']
    #print("resp_type: " + mobile_reponse_type)
    try:
        if hil_flow_control_packets['mobile_response']['views']['type'] != "dollartopgainer_list":
            print("Error: " + "mobile_response_type error. " + "it is not what is intended to be")
    except:
        print("mobile_reponse_type fetch error. Some problem in json file format")

    #print("resp_data_symbols: " + str(resp_data_symbols))

    try:
        resp_data_symbols = hil_flow_control_packets['mobile_response']['views']['data']['symbols']
        # if all the items in the list of response_data_symbols are not string then throw error
        if all(isinstance(item, str) for item in resp_data_symbols) == False:
            print("Error: " + "mobile_response_data_symbols are not strings.")
    except:
        print("mobile_reponse data symbols fetch error. Some problem in json file format")


    try:
        if hil_flow_control_packets['mobile_response']['references'][0]['type'] != "instruments":
            print("Error: " + "mobile_response_references_type error. " + "it is not what is intended to be")
    except:
        print("mobile_reponse_references_type fetch error. Some problem in json file format")

    #print("references_type: " + references_type)

    for packet in hil_flow_control_packets['mobile_response']['references'][0]['data']:
        check_data_references_values(packet)
        #print("references_data_packet_1: " + str(references_data_packet_1))


    #if self.hil_overflow > 0:
        #self.log.info("Overflow flag is set. Replay data error!")
        #print("\nOverflow flag error in Replay data in Frame number:{}".format(
            #packet['_source']['layers']['frame']['frame.number']))
        #print(
            #"\nFor more information about frame and hil flow control values where it went wrong, please check the hil_flow_control.json file generated in the input_folder path given by you")
        #exit()



# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    json_automate("C:/Test/json_test")
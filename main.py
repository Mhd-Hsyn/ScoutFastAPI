# from fastapi import FastAPI

# app = FastAPI()

# @app.get('/')
# def read_root():
#     return {'message': 'Hello, Scout!'}

# if __name__ == '__main__':
#     import uvicorn
#     uvicorn.run(app, host='127.0.0.1', port=8000)





from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI, HTTPException, Response,Query
from pymongo import MongoClient
from bson import ObjectId 
import json
from typing import Optional
from fuzzywuzzy import process
from fuzzywuzzy import fuzz
from base_url import get_mongo_connection
import re
db = get_mongo_connection()
# collection = db["Scout"]

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["Authorization", "Content-Type"],
)



# @app.get("/playerdata")
# async def get_data():
#     # Retrieve data from MongoDB
#     data = list(collection.find())
#     return {"data": data}



query_data_collection = db["query-data"]
collection = db["leagues-data"]

query_data_collection = db["query-data"]
collection = db["leagues-data"]

@app.get("/data")
async def get_data(page: int = Query(..., ge=1), leagues: str = Query(None)):
    per_page = 12
    skip = (page - 1) * per_page
    if leagues:
        filter_query = {"leagues": leagues}
        total_docs = collection.count_documents(filter_query)
        all_data = list(collection.find(filter_query).skip(skip).limit(per_page))
    else:
        total_docs = collection.count_documents({})
        all_data = list(collection.find().skip(skip).limit(per_page))

    # Convert ObjectId to string for _id field
    for item in all_data:
        item["_id"] = str(item["_id"])
        item["Image_URL"] = item.pop("Image URL").replace(" ", "_")
        item["Href_value"] = item.pop("Href value").replace(" ", "_")
        item["uid"] = item.pop("uid")
        
        # Fetch details from "query-data" collection based on "uid" field
        leagues_uid = item["uid"]
        print("leagues_uid:", leagues_uid)
        query_data = query_data_collection.find({"leagues_uid": leagues_uid})
        # print("query_data:", query_data)
        if query_data:
            # Update the item with details from "query-data" collection
            for document in query_data_collection.find():
                query_data = {
                    "query_link": document.get("query_link"),
                    "leagues_text": document.get("leagues_text"),
                    "query": document.get("query"),
                    "leagues_uid": document.get("leagues_uid")
                }

                print("query_data:", query_data)

        else:
            print("No data found for leagues_uid:", leagues_uid)



    # Generate URLs for pagination
    total_pages = (total_docs + per_page - 1) // per_page
    next_page = page + 1 if page < total_pages else None
    prev_page = page - 1 if page > 1 else None
    next_page_url = f"/data?leagues={leagues}&page={next_page}" if next_page is not None else None
    prev_page_url = f"/data?leagues={leagues}&page={prev_page}" if prev_page is not None else None

    pagination = {
        "total_pages": total_pages,
        "next_page": next_page_url,
        "prev_page": prev_page_url
    }

    return {"data": all_data, "total_documents": total_docs, "pagination": pagination}



# @app.get('/get_players/{leagues_uid}')
# def get_players(leagues_uid: str, response: Response):
#     users_collection = db['query-data']
#     # print(users_collection,"_____________________________users_collection")

#     players = list(users_collection.find({"leagues_uid": leagues_uid}))
#     # print(players,"_____________________________players")
    
#     if players:
#         transformed_data = []
        
#         for player in players:
       
#                 player['_id'] = str(player['_id'])
#                 formatted_player = {
#                     "ObjectID": player['_id'],
#                     "query_uid": player['query_uid'],
#                     "query": player['query'],
#                     "leagues_text": player['leagues_text'],
#                     "query_link": player['query_link'],
#                     "query_url": player['image_url'],
#                     # "csvname": player['csv_name'],
#                     'table_data': player['table_data']  
#                 }

#                 # Check if the section already exists in transformed_data
#                 section_exists = False
#                 for section in transformed_data:
#                         section["AllTables"].append(formatted_player)
#                         section_exists = True
#                         break
                
#                 # If the section doesn't exist, create a new section
#                 if not section_exists:
#                     new_section = {
#                         "leagues_data": [formatted_player]
#                     }
#                     transformed_data.append(new_section)
        
#         if transformed_data:
#             data_json = json.dumps(transformed_data, default=json_serialization)
#             response.body = data_json.encode('utf-8')
#             response.headers['Content-Type'] = 'application/json'
#             response.status_code = 200
#             return response
#         else:
#             raise HTTPException(status_code=404, detail=f"No data found for section name and UID {leagues_uid}")
#     else:
#         raise HTTPException(status_code=404, detail="Players not found for the given UID")


# def json_serialization(obj):
#     if isinstance(obj, float) and (obj == float('inf') or obj == float('-inf') or obj != obj):
#         return None
#     elif isinstance(obj, bytes):
#         return obj.decode('utf-8')
#     else:
#         raise TypeError(f"Object of type")
#         item["Image_URL"] = item.pop("Image URL").replace(" ", "_")
#         item["Href_value"] = item.pop("Href value").replace(" ", "_")
    
#     # Generate URLs for pagination
#     total_pages = (total_docs + per_page - 1) // per_page
#     next_page = page + 1 if page < total_pages else None
#     prev_page = page - 1 if page > 1 else None
#     next_page_url = f"/data?leagues={leagues}&page={next_page}" if next_page is not None else None
#     prev_page_url = f"/data?leagues={leagues}&page={prev_page}" if prev_page is not None else None

#     pagination = {
#         "total_pages": total_pages,
#         "next_page": next_page_url,
#         "prev_page": prev_page_url
#     }

#     return {"data": data, "total_documents": total_docs, "pagination": pagination}


@app.get('/get_players/{leagues_uid}')
def get_players(leagues_uid: str, response: Response):
    users_collection = db['query-data']
    # print(users_collection,"_____________________________users_collection")

    players = list(users_collection.find({"leagues_uid": leagues_uid}))
    # print(players,"_____________________________players")
    
    if players:
        transformed_data = []
        
        for player in players:
       
                player['_id'] = str(player['_id'])
                formatted_player = {
                    "ObjectID": player['_id'],
                    "query_uid": player['query_uid'],
                    "query": player['query'],
                    "leagues_text": player['leagues_text'],
                    "query_link": player['query_link'],
                    "query_url": player['image_url'],
                    # "csvname": player['csv_name'],
                    'table_data': player['table_data']  
                }

            
                new_section = {
                    "leagues_data": [formatted_player]
                }
                transformed_data.append(new_section)
    
        if transformed_data:
            data_json = json.dumps(transformed_data, default=json_serialization)
            response.body = data_json.encode('utf-8')
            response.headers['Content-Type'] = 'application/json'
            response.status_code = 200
            return response
        else:
            raise HTTPException(status_code=404, detail=f"No data found for section name and UID {leagues_uid}")
    else:
        raise HTTPException(status_code=404, detail="Players not found for the given UID")


def json_serialization(obj):
    if isinstance(obj, float) and (obj == float('inf') or obj == float('-inf') or obj != obj):
        return None
    elif isinstance(obj, bytes):
        return obj.decode('utf-8')
    else:
        raise TypeError(f"Object of type {type(obj)} is not JSON serializable")
    

# ######################################### searchleagues #########################################################


@app.get('/search_leagues/{leagues_text}')
async def search_leagues(leagues_text: str, response: Response):
    users_collection = db['query-data']

    all_players = list(users_collection.find())

    print("------------------") 
    best_match, best_score = process.extractOne(leagues_text.lower(), [player['leagues_text'].lower() for player in all_players])
    

    if best_score > 0:
        best_document = next(player for player in all_players if player['leagues_text'].lower() == best_match)

        # print("Keys in best_document:", best_document.keys())

        formatted_player = {
            "ObjectID": str(best_document['_id']),
            "query_uid": best_document.get('query_uid', ''),
            "query": best_document.get('query', ''),
            "leagues_text": best_document.get('leagues_text', ''),
            "query_link": best_document.get('query_link', ''),
            "query_url": best_document.get('image_url', ''),
            "table_data": best_document.get('table_data', '')
        }

        for key in ['h2_text', 'span_text', 'p_text', 'p_text1']:
            if best_document.get(key):
                formatted_player[key] = best_document[key]

        print("Keys in formatted_player after adding:", formatted_player.keys())

        data_json = json.dumps(formatted_player, default=json_serialization)
        response.body = data_json.encode('utf-8')
        response.headers['Content-Type'] = 'application/json'
        response.status_code = 200
        return response
    else:
        raise HTTPException(status_code=404, detail=f"No data found for section name and UID {leagues_text}")

def json_serialization(obj):
    if isinstance(obj, float) and (obj == float('inf') or obj == float('-inf') or obj != obj):
        return None
    elif isinstance(obj, bytes):
        return obj.decode('utf-8')
    else:
        raise TypeError(f"Object of type {type(obj)} is not JSON serializable")


# # ######################################### suggestion_api #########################################################


@app.get('/suggestion_api/{leagues_text}')
async def suggest_leagues(leagues_text: str, response: Response):

    collection = db['playerdata']
    all_players = collection.find() 

    # Perform a simple string comparison to find matches
    matches = [player['leagues_text'] for player in all_players if leagues_text.lower() in player['leagues_text'].lower()]

    top_matches = matches[:5]

    if top_matches:
        response_data = {
            "top_5_leagues_text": top_matches
        }

        data_json = json.dumps(response_data)
        response.body = data_json.encode('utf-8')
        response.headers['Content-Type'] = 'application/json'
        response.status_code = 200
        return response
    else:
        raise HTTPException(status_code=404, detail=f"No data found for leagues_text: {leagues_text}")




@app.get('/get_players_profiles/{leagues_text}')
def get_players_data(leagues_text: str):

    def extract_names(text):
        potential_names = re.findall(r"[A-Z][a-z]* [A-Z][a-z]*", text)
        potential_names.extend(re.findall(r"[a-z][a-z]* [A-Z][a-z]*", text))  # Add condition for names starting with lowercase letter
        potential_names.extend(re.findall(r"\b[A-Z][a-z]*\b", text))  
        potential_names = [name[:1].lower() + name[1:] for name in potential_names]
        potential_names.extend([name.upper() for name in potential_names])
        return potential_names

    names = extract_names(leagues_text)

    users_collection = db['players_profile']
    players = []
    for name in names:
        regex_name = re.compile("^" + re.escape(name) + "$", re.IGNORECASE)
        players.extend(list(users_collection.find({"Heading": {"$regex": regex_name}})))

    if not players:
        raise HTTPException(status_code=404, detail="Players not found for the given leagues_text")

    transformed_data = []
    for player in players:
        player['_id'] = str(player['_id'])
        formatted_player = {
            "Page": player['folder_name'],
            "Heading": player['Heading'],
            "Profile": player['Profile'],
            "Profile1": player['Profile1'],
            "Span": player['Span'],
            "Image_URLs": player['Image URLs'],
            "PlayerUID": player['uuid'],
            "ObjectID": player['_id'],
            "Data": player['data'],
            "NewDocument": True
        }

        transformed_data.append(formatted_player)

    return transformed_data

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=1008, reload=True)



# from fastapi import FastAPI

# app = FastAPI()

# @app.get('/')
# def read_root():
#     return {'message': 'Hello, Scout!'}

# if __name__ == '__main__':
#     import uvicorn
#     uvicorn.run(app, host='127.0.0.1', port=8000)



import uvicorn
import os
from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI, HTTPException, Response,Query
from pymongo import MongoClient
from bson import ObjectId 
import json
from typing import Optional
from base_url import get_mongo_connection
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




# @app.get('/get_players/{player_uid}')
# def get_players(player_uid: str, response: Response, section_name: Optional[str] = None):
#     users_collection = db['folder_data']
#     players = list(users_collection.find({"player_uid": player_uid}))
    
#     if not section_name:
#         # Return all section names for the given UID
#         if players:
#             section_names = set()
#             for player in players:
#                 section_names.add(player['section_name'])
#             return {"SectionNames": list(section_names)}
#         else:
#             raise HTTPException(status_code=404, detail="No sections found for the given UID")
    
#     else:
#         # Return data for the specified section name and UID
#         if players:
#             transformed_data = []
            
#             for player in players:
#                 if player['section_name'] == section_name:
#                     player['_id'] = str(player['_id'])
#                     formatted_player = {
#                         "Sectionname": player['section_name'],
#                         "PlayerName": player['player_name'],
#                         "PlayerUID": player['player_uid'],
#                         "ObjectID": player['_id'],
#                         # "csvname": player['csv_name'],
#                         player['csv_name']: player['data']  
#                     }

#                     # Check if the section already exists in transformed_data
#                     section_exists = False
#                     for section in transformed_data:
#                         if section["Sectionname"] == section_name:
#                             section["AllTables"].append(formatted_player)
#                             section_exists = True
#                             break
                    
#                     # If the section doesn't exist, create a new section
#                     if not section_exists:
#                         new_section = {
#                             "Sectionname": section_name,
#                             "AllTables": [formatted_player]
#                         }
#                         transformed_data.append(new_section)
            
#             if transformed_data:
#                 data_json = json.dumps(transformed_data, default=json_serialization)
#                 response.body = data_json.encode('utf-8')
#                 response.headers['Content-Type'] = 'application/json'
#                 response.status_code = 200
#                 return response
#             else:
#                 raise HTTPException(status_code=404, detail=f"No data found for section name {section_name} and UID {player_uid}")
#         else:
#             raise HTTPException(status_code=404, detail="Players not found for the given UID")


# def json_serialization(obj):
#     if isinstance(obj, float) and (obj == float('inf') or obj == float('-inf') or obj != obj):
#         return None
#     elif isinstance(obj, bytes):
#         return obj.decode('utf-8')
#     else:
#         raise TypeError(f"Object of type {type(obj)} is not JSON serializable")


collection = db["leagues-data"]


@app.get("/data")
async def get_data(page: int = Query(..., ge=1), leagues: str = Query(None)):
    per_page = 12
    skip = (page - 1) * per_page
    if leagues:
        filter_query = {"leagues": leagues}
        total_docs = collection.count_documents(filter_query)
        data = list(collection.find(filter_query).skip(skip).limit(per_page))
    else:
        total_docs = collection.count_documents({})
        data = list(collection.find().skip(skip).limit(per_page))

    # Convert ObjectId to string for _id field
    for item in data:
        item["_id"] = str(item["_id"])
        item["Image_URL"] = item.pop("Image URL").replace(" ", "_")
        item["Href_value"] = item.pop("Href value").replace(" ", "_")
    
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

    return {"data": data, "total_documents": total_docs, "pagination": pagination}


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

                # Check if the section already exists in transformed_data
                section_exists = False
                for section in transformed_data:
                        section["AllTables"].append(formatted_player)
                        section_exists = True
                        break
                
                # If the section doesn't exist, create a new section
                if not section_exists:
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


@app.get('/search_leagues/{leagues_text}')
def search_leagues(leagues_text: str, response: Response):
    users_collection = db['query-data']

    players = list(users_collection.find({"leagues_text": leagues_text}))
    
    if players:
        transformed_data = []
        
        for player in players:
            player['_id'] = str(player['_id'])

            # Create a dictionary with non-empty values
            formatted_player = {
                "ObjectID": player['_id'],
                "query_uid": player.get('query_uid', ''),
                "query": player.get('query', ''),
                "leagues_text": player.get('leagues_text', ''),
                "query_link": player.get('query_link', ''),
                "query_url": player.get('image_url', ''),
                "table_data": player.get('table_data', '')
            }

            # Check if the section already exists in transformed_data
            section_exists = False
            for section in transformed_data:
                if section["leagues_data"][0]['leagues_text'] == player['leagues_text']:
                    section["leagues_data"].append(formatted_player)
                    section_exists = True
                    break
                
            # If the section doesn't exist, create a new section
            if not section_exists:
                new_section = {
                    "leagues_data": [formatted_player]
                }
                transformed_data.append(new_section)

            # Add keys with non-empty values below table_data
            for key in ['h2_text', 'span_text', 'p_text', 'p_text1']:
                if player.get(key):
                    formatted_player[key] = player[key]

        if transformed_data:
            data_json = json.dumps(transformed_data, default=json_serialization)
            response.body = data_json.encode('utf-8')
            response.headers['Content-Type'] = 'application/json'
            response.status_code = 200
            return response
        else:
            raise HTTPException(status_code=404, detail=f"No data found for section name and UID {leagues_text}")
    else:
        raise HTTPException(status_code=404, detail="Players not found for the given Leagues")


def json_serialization(obj):
    if isinstance(obj, float) and (obj == float('inf') or obj == float('-inf') or obj != obj):
        return None
    elif isinstance(obj, bytes):
        return obj.decode('utf-8')
    else:
        raise TypeError(f"Object of type {type(obj)} is not JSON serializable")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)



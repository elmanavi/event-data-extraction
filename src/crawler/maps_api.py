from dataclasses import fields
import streamlit as st
from google.maps import places_v1



def get_maps_results(query, location):
    # Create a client
    client = places_v1.PlacesClient(client_options={"api_key": st.secrets["google_maps_api"]["api_key"]})

    # Initialize request argument(s)
    request = places_v1.SearchTextRequest(
        text_query=f"{query} in {location}",
        included_type=query
    )

    fieldMask = "places.displayName,places.websiteUri,places.formattedAddress,places.types"
    # Make the request
    response = client.search_text(request=request, metadata=[("x-goog-fieldmask",fieldMask)])
    return response.places

get_maps_results("library", "Nürnberg")
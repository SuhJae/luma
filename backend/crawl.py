from concurrent.futures import ThreadPoolExecutor, as_completed
from kheritageapi.palace import PalaceSearcher, PalaceInfo
from kheritageapi.models import PalaceCode
from app.db import LumaDB

db = LumaDB()
palaces = [PalaceCode.GYEONGBOKGUNG, PalaceCode.CHANGDEOKGUNG, PalaceCode.CHANGGYEONGGUNG, PalaceCode.DEOKSUGUNG, PalaceCode.JONGMYO]


def save_palace_details(item):
    try:
        palace_info = PalaceInfo(item).retrieve_details()
        return db.save_palace(palace_info, overwrite=False)
    except Exception as e:
        print(f"Error saving palace details: {e}")
        return None


for palace in palaces:
    search = PalaceSearcher(palace)
    items = search.perform_search()

    # Define the number of threads to use
    num_threads = 10  # Adjust this number based on your system and network capabilities

    with ThreadPoolExecutor(max_workers=num_threads) as executor:
        # Submit all tasks to the executor
        future_to_item = {executor.submit(save_palace_details, item): item for item in items}

        # Process the results as they complete
        for future in as_completed(future_to_item):
            item = future_to_item[future]
            try:
                result = future.result()
                if result:
                    print(f"Palace saved successfully: {result}")
                else:
                    print(f"Failed to save palace: {item}")
            except Exception as exc:
                print(f"Palace generated an exception: {exc}")

    print("All palaces processed.")

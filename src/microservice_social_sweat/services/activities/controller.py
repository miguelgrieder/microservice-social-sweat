from typing import Any

from fastapi import Request

from microservice_social_sweat.services.activities.models import Filter

activities_dummy_data = [
    {
        "id": "14864910",
        "name": "Downtown Fitness Hub",
        "description": "State-of-the-art fitness center in the heart of downtown. Our gym offers the latest equipment, personal training, and various fitness classes. Open 24/7 for your convenience. We provide a clean and welcoming environment to help you reach your fitness goals. From weightlifting to cardio machines, we have it all.",
        "medium_url": "https://ironberg.com.br/assets/images/ironberg-sp-3.jpeg",
        "review_scores_rating": 100,
        "activity_type": "Public Spot",
        "price": 50,
        "smart_location": "Berlin, Germany",
        "number_of_reviews": 14,
        "host_picture_url": "https://a0.muscache.com/im/pictures/43518019/ead2dbb7_original.jpg?aki_policy=x_large",
        "host_name": "Monica",
        "host_since": "2015-06-15",
        "listing_url": "https://www.com/activity/14864910",
        "xl_picture_url": "https://ironberg.com.br/assets/images/ironberg-sp-3.jpeg",
        "participants": 240,
        "geometry": {"type": "Point", "coordinates": [13.362449647584155, 52.48895019165655]},
        "sport_type": "weight-lifter",
    },
    {
        "id": "3393282",
        "name": "Evening Yoga Class",
        "description": "Unwind with our evening yoga session. Experience a gentle flow designed to release tension, calm your mind, and prepare your body for restful sleep. Our experienced instructor will guide you through a series of poses and breathing exercises tailored to all skill levels. Whether you're looking to de-stress after a long day or enhance your overall well-being, this session offers the perfect balance of relaxation and rejuvenation. Join us and embrace the peaceful ambiance, leaving you refreshed and ready for the day ahead.",
        "medium_url": "https://www.ymcaclub.co.uk/wp-content/uploads/2023/05/Supple_Strenght-34-1024x684.jpg",
        "review_scores_rating": 99,
        "activity_type": "Public Session",
        "price": 75,
        "smart_location": "Berlin, Germany",
        "number_of_reviews": 18,
        "host_picture_url": "https://a0.muscache.com/im/users/17119078/profile_pic/1403904832/original.jpg?aki_policy=profile_x_medium",
        "host_name": "Stefanie",
        "host_since": "2014-06-22",
        "listing_url": "https://www.com/activity/3393282",
        "xl_picture_url": "https://www.ymcaclub.co.uk/wp-content/uploads/2023/05/Supple_Strenght-34-1024x684.jpg",
        "participants": 2,
        "geometry": {"type": "Point", "coordinates": [13.36255769672526, 52.548872817489354]},
        "sport_type": "yoga",
    },
    {
        "id": "7885622",
        "name": "Newbie Soccer Cup",
        "description": "Join us for the inaugural Newbee Soccer Cup, a thrilling new sports event designed to bring together soccer enthusiasts of all skill levels! This exciting tournament offers a platform for amateur teams to showcase their talent, compete in a friendly yet competitive environment, and foster a sense of community and sportsmanship.\n",
        "medium_url": "https://s2-ge.glbimg.com/AApE5gEe4YHuPloai7nojxAoTug=/0x0:719x476/984x0/smart/filters:strip_icc()/s.glbimg.com/es/ge/f/original/2014/09/21/final_copa_oeste.jpg",
        "review_scores_rating": 99,
        "activity_type": "Event",
        "price": 50,
        "smart_location": "Berlin, Germany",
        "number_of_reviews": 38,
        "host_picture_url": "https://a0.muscache.com/im/pictures/0acc35e0-67b3-4a80-b257-56052b290f1e.jpg?aki_policy=profile_x_medium",
        "host_name": "Mikael",
        "host_since": "2015-02-22",
        "listing_url": "https://www.com/activity/7885622",
        "xl_picture_url": "https://s2-ge.glbimg.com/AApE5gEe4YHuPloai7nojxAoTug=/0x0:719x476/984x0/smart/filters:strip_icc()/s.glbimg.com/es/ge/f/original/2014/09/21/final_copa_oeste.jpg",
        "participants": 23,
        "geometry": {"type": "Point", "coordinates": [13.456734695054609, 52.514191929150456]},
        "sport_type": "soccer",
    },
    {
        "id": "1563562",
        "name": "IronMan Delray",
        "description": "Challenge yourself with the ultimate endurance event at IronMan Delray. Set against the beautiful backdrop of Delray Beach, this triathlon pushes athletes to their limits with a grueling combination of swimming, cycling, and running. Whether you're a seasoned triathlete or taking on your first IronMan, this event offers a supportive and electrifying atmosphere. With well-marked courses, top-notch facilities, and enthusiastic spectators, IronMan Delray promises an unforgettable experience that will test your strength, stamina, and determination. Finish strong and earn your place among the IronMan elite.",
        "medium_url": "https://orkilacapital.com/wp-content/uploads/2023/09/IM-Finish.jpg",
        "review_scores_rating": 96,
        "activity_type": "Event",
        "price": 45,
        "smart_location": "Berlin, Germany",
        "number_of_reviews": 71,
        "host_picture_url": "https://a0.muscache.com/im/users/8319062/profile_pic/1402827631/original.jpg?aki_policy=profile_x_medium",
        "host_name": "Sven",
        "host_since": "2013-08-22",
        "listing_url": "https://www.com/activity/1563562",
        "xl_picture_url": "https://orkilacapital.com/wp-content/uploads/2023/09/IM-Finish.jpg",
        "participants": 43,
        "geometry": {"type": "Point", "coordinates": [13.34589882667451, 52.499586830677025]},
        "sport_type": "run-fast",
    },
]


def filter_activities(request: Request, filter: Filter) -> Any:
    if filter.activity_id:
        activities = None
        for ac in activities_dummy_data:
            if int(ac["id"]) == filter.activity_id:
                activities = [ac]
                break
    else:
        activities = activities_dummy_data
    return {"activities": activities}

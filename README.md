# hotel-hunter
hotel recommender system with Django
[www.HotelHunter.com](http://panapotproject.pythonanywhere.com/)

Implemented with algorithm __"Dynamic ranking of hotels features depending on context"__.
It can provide different recommendation when variation of context sets are acquired by target user.
It's hybrid recommendation that considered context aware of target user by using Point Of Interest [POI](https://en.wikipedia.org/wiki/Point_of_interest), trip types and companions same as tripadvisor to recommend hotel follow by user preference. 
[Research](http://panapot.pythonanywhere.com/) is coming soon

### Sign In
	username: user1, password: 1234
### Search:
	[Bangkok, Singapore, Tokyo]
### Trip type:
	[Business, Leisure]
### Companion:
	[Solo, Friend, Couple, Family]
	
### Features:
* Member system
* Search hotels
* Filter hotel results by
* Sort hotel results by
* Review and Rating Function
* __Recommender system *__

### Dataset: [rec.sql](https://github.com/9Ten/hotel-hunter/blob/master/rec.sql)
* 50 users
* 1500 records
* 350 hotels

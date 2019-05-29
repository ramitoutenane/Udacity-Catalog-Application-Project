from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database_setup import Base, Category, Item, User

engine = create_engine('sqlite:///catalog.db')
Base.metadata.bind = engine
DBSession = sessionmaker(bind=engine)
session = DBSession()

# User to add initial data
rami = User(id=1, name='Rami',
            email='mhtoutenane119@cit.just.edu.jo')
session.add(rami)
session.commit()

# soccer Category and Items
soccer = Category(id=1, name='Soccer')
session.add(soccer)
session.commit()

cleat = Item(id=1, name='Cleat', category_id=1, user_id=1,
             description='Shoes worn when playing soccer')
session.add(cleat)
session.commit()

soccer_ball = Item(id=2, name='Soccer Ball', category_id=1, user_id=1,
                   description='Ball used in playing soccer')
session.add(soccer_ball)
session.commit()

jersey = Item(id=3, name='Jersey', category_id=1, user_id=1,
              description='The official shirt')
session.add(jersey)
session.commit()

# basketball Category and Items
basketball = Category(id=2, name='Basketball')
session.add(basketball)
session.commit()

basket_ball = Item(id=4, name='Basketball', category_id=2, user_id=1,
                   description='Ball used in playing basketball')
session.add(basket_ball)
session.commit()

sneakers = Item(id=5, name='Sneakers', category_id=2, user_id=1,
                description='Shoes worn when playing basketball')
session.add(sneakers)
session.commit()

# baseball Category and Items
baseball = Category(id=3, name='Baseball')
session.add(baseball)
session.commit()

base_ball = Item(id=6, name='Baseball', category_id=3, user_id=1,
                 description='Ball used in playing baseball')
session.add(base_ball)
session.commit()

bat = Item(id=7, name='Bat', category_id=3, user_id=1,
           description='smooth wooden or metal club used to hit the ball')
session.add(bat)
session.commit()

gloves = Item(id=8, name='Gloves', category_id=3, user_id=1,
              description='large leather glove worn by defending team')
session.add(gloves)
session.commit()

# tennis Category and Items
tennis = Category(id=4, name='Tennis')
session.add(tennis)
session.commit()

tennis_ball = Item(id=9, name='Tennis Ball', category_id=4, user_id=1,
                   description='Ball used in playing tennis')
session.add(tennis_ball)
session.commit()

racket = Item(id=10, name='Racket', category_id=4, user_id=1,
              description='Used for striking a tennis ball')
session.add(racket)
session.commit()

# snowboarding Category and Items
snowboarding = Category(id=5, name='Snowboarding')
session.add(snowboarding)
session.commit()

snowboard = Item(id=11, name='Snowboard', category_id=5, user_id=1,
                 description='Board with ability to glide on snow')
session.add(snowboard)
session.commit()

goggles = Item(id=12, name='Goggles', category_id=5, user_id=1,
               description='Item to protect the eye')
session.add(goggles)
session.commit()

print "Finished Adding Data"

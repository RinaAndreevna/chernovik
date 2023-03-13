import sqlalchemy
import datetime
from sqlalchemy.orm import sessionmaker

from models import Users, Candidates, Photos
from vk_config import DSN


engine = sqlalchemy.create_engine(DSN)
Session = sessionmaker(bind=engine)


def insert_user(session, vk_id, name, age, city, sex):
    if not session.query(Users.vk_id).filter(Users.vk_id == str(vk_id)).all():
        table_users = Users(vk_id=vk_id,
                            name=name,
                            age=datetime.datetime.now().year - age,
                            city=city, sex=sex,
                            )
        session.add(table_users)
    session.commit()


def insert_candidates(session, vk_id, name, age, city, sex, favorite, user):
    if not session.query(Candidates.vk_id).filter(Candidates.vk_id == str(vk_id)).all():
        table_candidates = Candidates(vk_id=vk_id,
                                      name=name,
                                      age=age,
                                      city=city,
                                      sex=sex,
                                      favorite=favorite,
                                      user_id=user,
                                      )
        session.add(table_candidates)
    session.commit()


def insert_photos(session, link, candidate_id):
    table_photos = Photos(link=link,
                          candidate_id=candidate_id,
                          )
    session.add(table_photos)
    session.commit()


def show_favorite(session, user_id):
    favorite_list = session.query(Candidates.vk_id).join(Users, Users.id == Candidates.user_id).filter(Users.vk_id == user_id).filter(Candidates.favorite == True).all()
    result = ''
    photos = []

    for i in favorite_list:
        candidate_name = session.query(Candidates.name).filter(Candidates.vk_id == i[0]).all()
        photo = session.query(Photos.link).join(Candidates, Candidates.id == Photos.candidate_id).filter(Candidates.vk_id == i[0]).all()
        photos.append(photo)
        result += f'\nName: {candidate_name[0][0]}\nAccount: https://vk.com/id{i[0]};'

    session.commit()

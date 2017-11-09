import milkmaid
from datetime import datetime


testToken = "1a79ee75e7328538f9df96bdc7e22f9d17ae398e"

def uploadMemento(mementoToken=testToken, mementoTime=datetime.now()):
    milkmaid.token = mementoToken
    mev = milkmaid.MementoEvent()
    mev.datetime = mementoTime.replace(microsecond=0)
    mev.create()
    
    #print("Memento Result: ", mev.id, mev.deployment, mev.datetime, mev.unread)
    
#     mev_list = milkmaid.MementoEvent.list()
#     print(mev_list)
#     print(mev_list[3].id,mev_list[3].deployment,mev_list[3].datetime, mev_list[3].unread )


def uploadAgitation(agitationToken=testToken, agitationTime=datetime.now(), agitationType=1):
    milkmaid.token = agitationToken
    new_notification = milkmaid.AthenaNotification()
    new_notification.event_time = agitationTime.replace(microsecond=0)
    new_notification.nottype = agitationType #1234
    new_notification.create()
    
    #notifiTypes = milkmaid.AthenaNotifyType.list()
    #notifyTypes[].id, notifyTypes[].title, notifyTypes[].detail
    
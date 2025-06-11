from vtc import db_yt_interface

api_service = db_yt_interface.PrepareAPI(filepath='../data/api_quota_state.json')
api_service.reset_and_reload_quotas()
print("Quota state has been reset")
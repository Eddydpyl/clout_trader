import tools.seller as seller
import tools.api as api

if __name__ == '__main__':
    response = api.get_profiles()
    profiles = response['ProfilesFound']
    next = response['NextPublicKey']

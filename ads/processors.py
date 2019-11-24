from ads.models import CommunityAd


def community_ad(request):
    return {'community_ad': CommunityAd.objects.first()}

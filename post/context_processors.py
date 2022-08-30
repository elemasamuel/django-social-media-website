from .models import Story


def story_links(request):
    story = Story.objects.all()
    return {'stories': story}
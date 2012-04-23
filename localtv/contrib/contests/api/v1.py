# Miro Community - Easiest way to make a video website
#
# Copyright (C) 2009, 2010, 2011, 2012 Participatory Culture Foundation
# 
# Miro Community is free software: you can redistribute it and/or modify it
# under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or (at your
# option) any later version.
# 
# Miro Community is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
# 
# You should have received a copy of the GNU Affero General Public License
# along with Miro Community.  If not, see <http://www.gnu.org/licenses/>.

from django.conf import settings
from django.conf.urls.defaults import url, include
from django.core.exceptions import ObjectDoesNotExist, MultipleObjectsReturned

from tastypie import fields
from tastypie.authentication import BasicAuthentication
from tastypie.authorization import Authorization
from tastypie.http import HttpGone, HttpMultipleChoices
from tastypie.resources import ModelResource

from localtv.api.v1 import api, UserResource, VideoResource
from localtv.contrib.contests.models import Contest, ContestVote


class ContestResource(ModelResource):
    votes = fields.ToManyField(
                'localtv.contrib.contests.api.v1.ContestVoteResource',
                'votes')
    videos = fields.ToManyField(VideoResource, 'videos')

    class Meta:
        queryset = Contest.objects.filter(site=settings.SITE_ID)


class ContestVoteResource(ModelResource):
    contest = fields.ToOneField(ContestResource, 'contest')
    video = fields.ToOneField(VideoResource, 'video')
    user = fields.ToOneField(UserResource, 'user')
    vote = fields.IntegerField('vote')

    class Meta:
        queryset = ContestVote.objects.filter(contest__site=settings.SITE_ID)
        authorization = Authorization()
        authentication = BasicAuthentication()

    def get_object_list(self, request):
        qs = super(ContestVoteResource, self).get_object_list(request)
        if hasattr(request, 'user') and request.user.is_authenticated():
            qs = qs.filter(user=request.user)
        return qs

    def obj_create(self, bundle, request=None, **kwargs):
        if hasattr(request, 'user') and request.user.is_authenticated():
            kwargs['user'] = request.user
        return super(ContestVoteResource, self).obj_create(bundle,
                                                           request=request,
                                                           **kwargs)


api.register(ContestResource())
api.register(ContestVoteResource())

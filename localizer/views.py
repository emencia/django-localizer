# -*- coding: UTF-8 -*-
#
# This program is free software: you can redistribute it and/or modify it
# under the terms of the GNU Lesser General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

# Import from Django
from django.http import HttpResponseRedirect
from django.utils.translation import activate, ugettext
from django.views.generic import TemplateView

# Import from Django-Localizer
from models import Message



class RemoveEmpty(TemplateView):
    template_name = 'localizer/message/remove_empty.html'

    def post(self, request, *args, **kw):
        Message.objects.filter(translation=u'').delete()
        return HttpResponseRedirect('.')


class AddLanguage(TemplateView):
    template_name = 'localizer/message/add_language.html'

    def post(self, request, *args, **kw):
        language = request.POST['language']
        activate(language)

        msgids = Message.objects.values_list('msgid', flat=True).distinct()
        missing = set(msgids) - set(msgids.filter(language=language))
        for msgid in missing:
            ugettext(msgid)

        return HttpResponseRedirect('.')

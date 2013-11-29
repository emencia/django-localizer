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

# Import
from django.db.models import Model
from django.db.models import BooleanField, CharField, TextField
from django.utils.translation import ugettext_lazy as _


modified_help = _(
    u'This field is automatically set to True when the translation is '
    u'modified through the admin interface.')

class Message(Model):

    msgid = TextField()
    msgstr = TextField(blank=True)
    language = CharField(max_length=20)

    # If True, this entry has been modified through the admin interface
    modified = BooleanField(default=False, help_text=modified_help)

    class Meta:
        unique_together = ('msgid', 'language')

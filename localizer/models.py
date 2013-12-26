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
from django.db.models import Model
from django.db.models import CharField, TextField
from django.utils.translation import ugettext_lazy as _


class Message(Model):

    msgid       = TextField()
    language    = CharField(max_length=20)
    msgstr      = TextField(help_text=_(
        u'This is the translation as found in the PO file from the source'
        u' code.'))

    # The user filled translation
    translation = TextField(blank=True)

    class Meta:
        unique_together = ('msgid', 'language')

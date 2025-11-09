"""Fetch SubD geometry from Grasshopper HTTP server."""

import requests
import cpp_core
from typing import Optional, Dict, Any


class SubDFetcher:
    """Fetch SubD control cage from Grasshopper server."""

    def __init__(self, host='localhost', port=8888):
        """Initialize fetcher.

        Args:
            host: Server hostname
            port: Server port
        """
        self.host = host
        self.port = port
        self.base_url = f'http://{host}:{port}'

    def is_server_available(self) -> bool:
        """Check if server is running."""
        try:
            response = requests.get(
                f'{self.base_url}/status',
                timeout=1
            )
            return response.status_code == 200
        except:
            return False

    def fetch_control_cage(self) -> Optional[cpp_core.SubDControlCage]:
        """Fetch SubD control cage from server.

        Returns:
            SubDControlCage if successful, None otherwise
        """
        try:
            response = requests.get(
                f'{self.base_url}/geometry',
                timeout=5
            )
            response.raise_for_status()

            data = response.json()

            # Convert JSON to SubDControlCage
            cage = cpp_core.SubDControlCage()

            # Add vertices
            for v in data['vertices']:
                cage.vertices.append(
                    cpp_core.Point3D(v[0], v[1], v[2])
                )

            # Add faces
            cage.faces = data['faces']

            # Add creases if present
            if 'creases' in data:
                for c in data['creases']:
                    cage.creases.append((c[0], c[1], c[2]))

            return cage

        except Exception as e:
            print(f"Failed to fetch geometry: {e}")
            return None

    def get_metadata(self) -> Optional[Dict[str, Any]]:
        """Get geometry metadata without full download."""
        try:
            response = requests.get(
                f'{self.base_url}/geometry',
                timeout=2
            )
            data = response.json()
            return data.get('metadata', {})
        except:
            return None

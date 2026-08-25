import requests
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny

class KatamerosTodayView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        from datetime import datetime

        today = datetime.now().strftime("%d-%m-%Y")

        url = f"https://api.katameros.app/readings/gregorian/{today}"

        params = {
            "languageId": 3,
            "bibleId": 11,
        }

        response = requests.get(
            url,
            params=params,
            timeout=10,
        )

        response.raise_for_status()

        return Response(response.json())
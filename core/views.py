import requests
from datetime import datetime

from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny


class KatamerosTodayView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):

        # =========================
        # Today's date
        # =========================
        now = datetime.now()

        gregorian_date = now.strftime("%d-%m-%Y")
        calendar_date = now.strftime("%Y-%m-%d")

        # =========================
        # Arabic month names
        # =========================
        gregorian_months = {
            1: "يناير",
            2: "فبراير",
            3: "مارس",
            4: "أبريل",
            5: "مايو",
            6: "يونيو",
            7: "يوليو",
            8: "أغسطس",
            9: "سبتمبر",
            10: "أكتوبر",
            11: "نوفمبر",
            12: "ديسمبر",
        }

        coptic_months = {
            "Tout": "توت",
            "Baba": "بابه",
            "Hator": "هاتور",
            "Kiahk": "كيهك",
            "Toba": "طوبة",
            "Amshir": "أمشير",
            "Baramhat": "برمهات",
            "Baramouda": "برمودة",
            "Bashans": "بشنس",
            "Paona": "بؤونة",
            "Epep": "أبيب",
            "Mesra": "مسرى",
            "Nasie": "النسيء",
        }

        # =========================
        # Gregorian date in Arabic
        # =========================
        gregorian_arabic = (
            f"{now.day} "
            f"{gregorian_months[now.month]} "
            f"{now.year}"
        )

        # =========================
        # Katameros - Readings
        # =========================
        readings_url = (
            f"https://api.katameros.app/readings/gregorian/{gregorian_date}"
        )

        readings_params = {
            "languageId": 3,
            "bibleId": 11,
        }

        readings_response = requests.get(
            readings_url,
            params=readings_params,
            timeout=10,
        )

        readings_response.raise_for_status()

        readings = readings_response.json()

        # =========================
        # Coptic.io - Coptic Date
        # =========================
        calendar_url = (
            f"https://api.coptic.io/api/calendar/{calendar_date}"
        )

        calendar_response = requests.get(
            calendar_url,
            timeout=10,
        )

        calendar_response.raise_for_status()

        calendar = calendar_response.json()

        # =========================
        # Coptic date in Arabic
        # =========================
        coptic_month = calendar.get("monthString", "")
        coptic_month_ar = coptic_months.get(
            coptic_month,
            coptic_month
        )

        coptic_arabic = (
            f"{calendar.get('day')} "
            f"{coptic_month_ar} "
            f"{calendar.get('year')}"
        )

        # =========================
        # Final Response
        # =========================
        return Response({
            "date": {
                "gregorian": gregorian_arabic,
                "coptic": coptic_arabic,
            },
            "readings": readings,
        })
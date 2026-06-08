from rest_framework import viewsets
from finances.transaction.models import Transaction
from finances.transaction.serializers import TransactionSerializer
from rest_framework.permissions import IsAuthenticated


class TransactionViewSet(viewsets.ModelViewSet):
    serializer_class = TransactionSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save()

    def get_queryset(self):
        user = self.request.user
        return Transaction.objects.filter(category__user=user)

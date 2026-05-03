from django.contrib import admin

from .models import Invoice, InvoiceItem, PaymentRecord


class InvoiceItemInline(admin.TabularInline):
    model = InvoiceItem
    extra = 1
    readonly_fields = ("total",)


class PaymentRecordInline(admin.TabularInline):
    model = PaymentRecord
    extra = 0


@admin.register(Invoice)
class InvoiceAdmin(admin.ModelAdmin):
    list_display = (
        "invoice_number",
        "client",
        "total_amount",
        "amount_paid",
        "status",
    )

    list_filter = ("status", "currency")

    search_fields = ("invoice_number", "client__name")

    readonly_fields = ("subtotal", "total_amount", "amount_paid", "status")

    readonly_fields = ("subtotal", "total_amount", "amount_paid", "status")

    inlines = [InvoiceItemInline, PaymentRecordInline]

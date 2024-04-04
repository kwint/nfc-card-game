from django.contrib import admin
from django.urls import reverse
from django.utils.html import format_html
from django.utils.safestring import mark_safe

from nfc_card_game.main.models import Mine, Player, Post, Team, TeamMine, PlayerItem, Item, PostRecipe 

# Register your models here.


class PlayerInLine(admin.TabularInline):
    model = Player


class TeamMineInLine(admin.TabularInline):
    model = TeamMine

class PlayerItemInline(admin.TabularInline):
    model = PlayerItem

class PostRecipeInline(admin.TabularInline):
    model = PostRecipe

class TeamMineAdmin(admin.ModelAdmin):
    list_display = ["mine", "team", "link"]

    @mark_safe
    def link(self, obj):
        card_url = reverse("mine", kwargs={"card_uuid": obj.card_uuid})
        return format_html(f'<a href="{card_url}">link</a>')

class TeamAdmin(admin.ModelAdmin):
    list_display = ["name"]
    inlines = [PlayerInLine]


class PlayerAdmin(admin.ModelAdmin):
    list_display = ["name", "card_uuid", "team", "section", "link"]
    inlines = [PlayerItemInline]

    @mark_safe
    def link(self, obj):
        card_url = reverse("player", kwargs={"card_uuid": obj.card_uuid})
        return format_html(f'<a href="{card_url}">link</a>')

class PlayerItemAdmin(admin.ModelAdmin):
    list_display = ["item", "player"]


class PostAdmin(admin.ModelAdmin):
    list_display = ["name", "card_uuid", "sells", "sell_amount", "link"]
    inlines = [PostRecipeInline]

    @mark_safe
    def link(self, obj):
        card_url = reverse("post", kwargs={"card_uuid": obj.card_uuid})
        return format_html(f'<a href="{card_url}">link</a>')


class MineAdmin(admin.ModelAdmin):
    list_display = ["name", "currency"]
    inlines = [TeamMineInLine]

class ItemAdmin(admin.ModelAdmin):
    list_display = ["name",]


class PostRecipeAdmin(admin.ModelAdmin):
    list_display = ['item', 'amount', 'post']

admin.site.register(Team, TeamAdmin)
admin.site.register(Player, PlayerAdmin)
admin.site.register(Post, PostAdmin)
admin.site.register(Mine, MineAdmin)
admin.site.register(TeamMine, TeamMineAdmin)
admin.site.register(PlayerItem, PlayerItemAdmin)
admin.site.register(Item, ItemAdmin)
admin.site.register(PostRecipe, PostRecipeAdmin)

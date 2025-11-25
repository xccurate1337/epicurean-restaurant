from django import forms
from .models import Блюдо, Категория

class БлюдоФорма(forms.ModelForm):
    class Meta:
        model = Блюдо
        fields = [
            'категория', 'тип_блюда', 'название', 'slug', 'описание',
            'цена', 'изображение', 'вес_объем', 'состав',
            'пищевая_ценность', 'время_приготовления', 'уровень_остроты',
            'теги', 'акция', 'цена_со_скидкой'
        ]
        widgets = {
            'описание': forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}),
            'состав': forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}),
            'пищевая_ценность': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '{"калории": 250, "белки": 15, "жиры": 10, "углеводы": 20}'
            }),
            'теги': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '["горячее", "мясо", "сытно"]'
            }),
            'категория': forms.Select(attrs={'class': 'form-select'}),
            'тип_блюда': forms.Select(attrs={'class': 'form-select'}),
            'название': forms.TextInput(attrs={'class': 'form-control'}),
            'slug': forms.TextInput(attrs={'class': 'form-control'}),
            'цена': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'изображение': forms.URLInput(attrs={'class': 'form-control'}),
            'вес_объем': forms.TextInput(attrs={'class': 'form-control'}),
            'время_приготовления': forms.NumberInput(attrs={'class': 'form-control'}),
            'уровень_остроты': forms.Select(attrs={'class': 'form-select'}),
            'акция': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'цена_со_скидкой': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
        }

    def clean_пищевая_ценность(self):
        данные = self.cleaned_data['пищевая_ценность']
        try:
            if isinstance(данные, str):
                import json
                json.loads(данные)
        except:
            raise forms.ValidationError("Введите корректный JSON формат")
        return данные

    def clean_теги(self):
        данные = self.cleaned_data['теги']
        try:
            if isinstance(данные, str):
                import json
                json.loads(данные)
        except:
            raise forms.ValidationError("Введите корректный JSON массив тегов")
        return данные
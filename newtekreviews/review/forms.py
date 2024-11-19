from django import forms
from captcha.fields import CaptchaField

from .models import Review, ReviewTopic, Category


class InitForm(forms.Form):
    def __init__(self, *args, **kwargs):
        """
        Initializes the form by setting all the field labels to empty strings.
        This is needed to hide the labels in the registration form.
        """
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            field.label = ""


class AddReviewForm(InitForm, forms.ModelForm):
    category = forms.ModelChoiceField(
        queryset=Category.objects.all(),
        empty_label="Category is not specified",
        label="Category"
        )

    class Meta:
        model = Review
        fields = [
            'title', 'description', 'main_image',
            'is_published', 'category'
            ]
        widgets = {
            'title': forms.TextInput(
                attrs={
                    'class': 'review-form__title-input text-input',
                    'placeholder': 'Review title'
                    }
                ),
            'description': forms.Textarea(
                attrs={
                    'class': 'review-form__description-input textarea-input',
                    'placeholder': 'Review description'
                    }
                ),
            'main_image': forms.FileInput(
                attrs={
                    'class': 'review-form__image-input file-input',
                    }
                ),
            'is_published': forms.CheckboxInput(attrs={
                'class': 'review-form__checkbox-input',
                'label': 'Published'
                    }
                ),
            'category': forms.Select(attrs={
                'class': 'review-form__select-input'
                    }
                ),
        }


class AddReviewTopicForm(forms.ModelForm):
    class Meta:
        model = ReviewTopic
        fields = ['review_topic_title', 'text_content']
        widgets = {
            'review_topic_title': forms.TextInput(
                attrs={
                    'class': 'review-form__title-input text-input',
                    'placeholder': 'Topic title'
                    }
                ),
            'text_content': forms.Textarea(
                attrs={
                    'class': 'review-form__description-input textarea-input',
                    'placeholder': 'Topic description'
                    }
                ),
        }


class EditReviewTopicForm(forms.ModelForm):
    class Meta:
        model = ReviewTopic
        fields = ['review_topic_title', 'text_content']
        widgets = {
            'review_topic_title': forms.TextInput(
                attrs={
                    'class': 'review-form__title-input text-input',
                    'placeholder': 'Topic title'
                    }
                ),
            'text_content': forms.Textarea(
                attrs={
                    'class': 'review-form__description-input textarea-input',
                    'placeholder': 'Topic description'
                    }
                ),
        }


ReviewTopicFormSet = forms.modelformset_factory(
    ReviewTopic, form=AddReviewTopicForm, extra=1, max_num=10
)
UpdateReviewTopicFormSet = forms.modelformset_factory(
    ReviewTopic, form=EditReviewTopicForm, extra=1, can_delete=True
)


class AddCategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ['name', 'category_background']


class ContactForm(InitForm, forms.Form):
    name = forms.CharField(
        max_length=100,
        widget=forms.TextInput(
            attrs={
                'class': 'contact-form__name-input text-input',
                'placeholder': 'Your name'
                }
            )
        )
    email = forms.EmailField(
        widget=forms.EmailInput(
            attrs={
                'class': 'contact-form__email-input text-input',
                'placeholder': 'Your email'
                }
            )
        )
    message = forms.CharField(
        widget=forms.Textarea(
            attrs={
                'class': 'contact-form__message-input textarea-input',
                'placeholder': 'Your message'
                }
            )
        )
    captcha = CaptchaField()


class CSVForm(forms.Form):
    csv_file = forms.FileField()

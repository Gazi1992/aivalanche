from pathlib import Path

# Package
package_path = Path(__file__).parent.absolute()

# Store
store_path = Path.joinpath(package_path, 'data_store')
dummy_data_path = Path.joinpath(store_path, 'DUMMY_DATA.json')

# Resources
resources_path = Path.joinpath(package_path, 'resources')

# Themes
themes_path = Path.joinpath(resources_path, 'themes')
theme_1_path = Path.joinpath(themes_path, 'theme_1.py')

# Images
images_path = Path.joinpath(resources_path, 'images')
logo_path = Path.joinpath(images_path, 'logo.png')
image_placeholder_path = Path.joinpath(images_path, 'image_placeholder.png')
project_card_background_path = Path.joinpath(images_path, 'background_example.jpg')
model_card_background_path = Path.joinpath(images_path, 'background_example_1.png')
projects_icon_path = Path.joinpath(images_path, 'projects_icon.png')
running_icon_path = Path.joinpath(images_path, 'running_icon.png')
search_icon_path = Path.joinpath(images_path, 'search_icon.png')
logout_icon_path = Path.joinpath(images_path, 'logout_icon.png')
plus_icon_path = Path.joinpath(images_path, 'plus_icon.png')
upload_icon_path = Path.joinpath(images_path, 'upload_icon.png')
arrow_down_icon_path = Path.joinpath(images_path, 'arrow_down_icon.png')
ascending_icon_path = Path.joinpath(images_path, 'ascending_icon.png')
descending_icon_path = Path.joinpath(images_path, 'descending_icon.png')
checkbox_checked_path = Path.joinpath(images_path, 'checkbox_checked.png')
checkbox_unchecked_path = Path.joinpath(images_path, 'checkbox_unchecked.png')
home_icon_path = Path.joinpath(images_path, 'home_icon.png')
log_x_icon_path = Path.joinpath(images_path, 'log_x_icon.png')
log_y_icon_path = Path.joinpath(images_path, 'log_y_icon.png')
lin_x_icon_path = Path.joinpath(images_path, 'lin_x_icon.png')
lin_y_icon_path = Path.joinpath(images_path, 'lin_y_icon.png')





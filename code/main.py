import StreetEasyWebScraping as sews

proj1 = sews.StreetEasyWebScraping()

print(proj1)

analysis_overwrite = True
download_overwrite = False

proj1.pull_active_listing(overwrite=False, listing_type='active_sales')
proj1.pull_active_listing(overwrite=False, listing_type='active_rentals')

proj1.update_active_listing_url_list()
proj1.update_building_url_list()

proj1.download_listing_pages(listing_type='active_sales', overwrite=download_overwrite)
proj1.download_listing_pages(listing_type='active_rentals', overwrite=download_overwrite)

if 1:
    proj1.download_building_pages(overwrite=False)

proj1.parse_building_page()  # get past sales and past rental url list

proj1.download_listing_pages(listing_type='past_sales', overwrite=download_overwrite)
proj1.download_listing_pages(listing_type='past_rentals', overwrite=download_overwrite)


proj1.parse_listing_page(listing_type='active_sales', overwrite=analysis_overwrite)
proj1.parse_listing_page(listing_type='active_rentals', overwrite=analysis_overwrite)
proj1.parse_listing_page(listing_type='past_sales', overwrite=analysis_overwrite)
proj1.parse_listing_page(listing_type='past_rentals', overwrite=analysis_overwrite)

print(proj1)

#proj1.download_building_pages(overwrite=False)


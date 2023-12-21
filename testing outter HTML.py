from base_code import *

shared_driver = Driver()

string = "<div class=""sc-57727bb1-8 bcbJAq swiper-button-prev"" tabindex=""0"" role=""button"" aria-label=""Previous slide""><div class=""sc-57727bb1-9 jQoqBQ swiper-buttons ipc-pager ipc-pager--visible ipc-pager--left ipc-pager--large"" role=""presentation""><svg width=""24"" height=""24"" xmlns=""http://www.w3.org/2000/svg"" class=""ipc-icon ipc-icon--chevron-left-inline ipc-icon--inline ipc-pager-icon"" viewBox=""0 0 24 24"" fill=""currentColor"" role=""presentation""><path d=""M18.378 23.369c.398-.402.622-.947.622-1.516 0-.568-.224-1.113-.622-1.515l-8.249-8.34 8.25-8.34a2.16 2.16 0 0 0 .548-2.07A2.132 2.132 0 0 0 17.428.073a2.104 2.104 0 0 0-2.048.555l-9.758 9.866A2.153 2.153 0 0 0 5 12.009c0 .568.224 1.114.622 1.515l9.758 9.866c.808.817 2.17.817 2.998-.021z""></path></svg></div></div>"
shared_driver.initialize()
shared_driver.load_site("https://www.imdb.com/")
site, outerHTML = shared_driver.all_html_elms[shared_driver.icon]
xpath = shared_driver.generate_xpath(outerHTML)
print(xpath)
# element = shared_driver.driver.find_element(By.XPATH, xpath)
# parent_node = element.find_element(By.XPATH, '..')
# print(parent_node.get_attribute("outerHTML"))


while 1:
    1
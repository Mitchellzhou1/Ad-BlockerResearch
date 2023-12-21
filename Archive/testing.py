# def test_elms(self, html_obj, tries=1):
#     ...
#     # attempts to click the button and refreshes afterward
#     try:
#         self.initial_outer_html = curr[self.icon].get_attribute('outerHTML')
#         self.initial_DOM = self.driver.page_source
#
#     except Exception as e:
#         self.icon += 1
#         continue
#
#     # this is filter but may not need...
#     if not self.cursor_change(curr[self.icon]):
#         self.icon += 1
#         continue
#
#     print("clicking on: ", self.initial_outer_html)
#     initial_tag = self.count_tags()
#
#     actions = ActionChains(self.driver)
#     actions.move_to_element(curr[self.icon]).perform()
#     self.click_button(curr[self.icon])
#
#     check = self.check_opened(self.url, curr[self.icon], initial_tag)
#
#     if check == "True - Redirect":
#         # outer_HTML_change = url
#         # Dom_change = new_url
#         write_results([check, '', '', self.initial_outer_html, '', '', '',
#                        self.url, self.driver.current_url, tries])
#     elif check == "True - outerHTML change":
#         write_results([check, self.outer_HTML_changed, self.DOM_changed, self.initial_outer_html,
#                        self.after_outer_html, '', '', '', '', tries])
#
#     elif check == "True? - DOM Change":
#         # need to figure out algo after find the difference
#         write_results([check, self.outer_HTML_changed, self.DOM_changed, self.initial_outer_html, '',
#                        "self.initial_DOM", "self.after_DOM", '', '', tries])
#
#     self.icon += 1
#
#     if self.icon >= len(curr):
#         self.icon = 0
#         break

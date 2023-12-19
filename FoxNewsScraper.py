import time
import random

from selenium.common.exceptions import NoSuchElementException

from browser import Browser
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
import csv
from bs4 import BeautifulSoup
import json


class TreeNode:
    def __init__(self, text, username, comment_time, depth=0, children=None):
        self.text = text
        self.username = username
        self.comment_time = comment_time
        self.children = children or []


# def write_tree_to_csv(node, csv_writer, depth=0):
#     print("write_tree_to_csv called")
#     print("writing data for username: ", node.username)
#     csv_writer.writerow([node.text, node.username, node.comment_time, depth])
#
#     depth = depth + 1
#     print("node.children.len: ", len(node.children))
#     for child in node.children:
#         print("child.username: ", child.username)
#         print("child.comment_time: ", child.comment_time)
#         write_tree_to_csv(child, csv_writer, depth=depth)


def print_tree(node, depth=0):
    with open('comment_tree.csv', 'a', newline='') as csv_file:
        csv_writer = csv.writer(csv_file)
        csv_writer.writerow(['Text', 'Username', 'Time', 'Depth'])
        write_tree_to_csv(node, csv_writer, depth=depth)


class FoxNewsScraper(object):
    def __init__(self, browser, depth):
        self.browser = browser
        self.depth = int(depth)

    def recursive_function(self, element_with_class_spcv_threadingline, depth=0, maxdepth=3):

        article_div_div = element_with_class_spcv_threadingline.find_element_by_class_name("spcv_root-message")

        # 3rd descedant child div of article (text)
        article_div_div_div = article_div_div.find_element_by_xpath(".//div")

        # Find elements within the root element
        username_element = article_div_div_div.find_element(By.CSS_SELECTOR, '.src-components-Username-index__wrapper')
        username = username_element.text
        # print("username: ", username)

        time_element = article_div_div_div.find_element(By.CSS_SELECTOR, '[data-spot-im-class="message-timestamp"]')
        comment_time = time_element.text
        # print("comment_time: ", comment_time)

        message_text_element = article_div_div_div.find_element(By.CSS_SELECTOR, '[data-spot-im-class="message-text"]')
        text = message_text_element.text

        print("username+depth")
        print(username, depth)

        node = TreeNode(text, username=username, comment_time=comment_time)
        if depth == maxdepth:
            return node

        print("iterate to expand show more replies")
        iterations = 0
        while iterations < 100:
            try:
                print("iterations: ", iterations)
                allchild_of_article_div_div = article_div_div.find_elements_by_xpath("./*")
                print("children.len: ", len(allchild_of_article_div_div))

                show_more_div = None
                # find show more button
                for child_element in allchild_of_article_div_div:
                    # Check if the target class is present in the class attribute
                    if 'spcv_show-more-replies' in child_element.get_attribute("class"):
                        show_more_div = child_element
                        print("show more div found")

                    if 'spcv_children-list' in child_element.get_attribute("class"):
                        li_list = child_element.find_elements_by_xpath("./*")
                        print("li_list.len: ", len(li_list))

                if show_more_div:
                    show_more_button = show_more_div.find_element_by_css_selector("button")
                    show_more_button.click()
                else:
                    raise NoSuchElementException("just to create an exception")
            except Exception as e:
                print("exception clicking show more replies button")
                break
            self.browser.implicitly_wait(10)
            iterations = iterations + 1
        print("break from while loop with iterations: ", iterations)

        # fix the getting li of next depth
        article_div_div_children = article_div_div.find_elements_by_xpath("./*")
        article_div_div_ul = [child_element for child_element in article_div_div_children if 'spcv_children-list' in child_element.get_attribute("class")]
        article_div_div_ul = article_div_div_ul[0]

        article_div_div_ul_li_list = article_div_div_ul.find_elements_by_xpath("./*")
        print("article_div_div_ul_li_list.len: ", len(article_div_div_ul_li_list))

        # create list of li for the user with given depth
        # article_div_div_taken_again = element_with_class_spcv_threadingline.find_element_by_class_name("spcv_root-message")
        # # article_div_div_ul_taken_again = article_div_div_taken_again.find_element_by_xpath('//ul[@class="spcv_children-list"]')
        # article_div_div_ul_taken_again = article_div_div_taken_again.find_element_by_css_selector('ul')
        # # print(article_div_div_ul_taken_again.get_attribute("innerHTML"))
        #
        #
        # first_level_li_elements_taken_again = article_div_div_ul_taken_again.find_elements_by_tag_name('li')
        # print("first_level_li_elements_taken_again.len: ", len(first_level_li_elements_taken_again))
        #
        # first_level_li_elements = []
        # if first_level_li_elements_taken_again:
        #     first_level_li_elements = article_div_div_ul_taken_again.find_elements_by_tag_name('li')
        #
        # print("len(first_level_li_elements): ", len(first_level_li_elements))

        print("call recursively the child of the user of depth depth")
        depth = depth + 1

        j = 0
        if len(article_div_div_ul_li_list) > 0:
            for li_element in article_div_div_ul_li_list:
                print("j: ", j)
                div_with_class_spcv_threadingLine = li_element.find_element_by_class_name("spcv_threadingLine")
                child_node = self.recursive_function(div_with_class_spcv_threadingLine, depth=depth)
                node.children.append(child_node)
                j = j + 1

        # j = 0
        # if len(first_level_li_elements) > 0:
        #     for li_element in first_level_li_elements:
        #         if j<10:
        #             div_with_class_spcv_threadingLine = li_element.find_element_by_class_name("spcv_threadingLine")
        #             child_node = self.recursive_function(div_with_class_spcv_threadingLine, depth=depth)
        #             node.children.append(child_node)
        #             j = j + 1
        print("returning node")
        return node

    def convert_tree_node_to_dict(self, node):
        # self.text = text
        # self.username = username
        # self.comment_time = comment_time
        # self.children = children or []
        return {'text': node.text, 'username': node.username,'comment_time': node.comment_time, 'children': [self.convert_tree_node_to_dict(child) for child in node.children]}

    def load_content(self, url):
        self.browser.get(url)
        self.browser.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(random.randrange(1, 5))

        # Set a timeout for the implicit wait (if needed)
        self.browser.implicitly_wait(10)  # You can adjust the timeout as needed
        messages_wrapper_div = WebDriverWait(self.browser, 20).until(
            EC.visibility_of_element_located((By.XPATH, '//div[@data-spotim-module="conversation"]'))
        )

        for i in range(20):
            print("clicking see more comments for i: ", i)
            try:
                print("clicking show more comments")
                # Click the button
                self.browser.execute_script(
                    """return document.querySelector('[data-spotim-module="conversation"][data-spot-im-module-default-area="conversation"]').querySelector('div').shadowRoot.querySelector('[class="spcv_loadMoreCommentsContainer"]').querySelector("button").click()"""
                )
                # wait 5 second to load the comments
                self.browser.implicitly_wait(10)
            except Exception as e:
                print("show more exception")
                print("break from for loop with i: ", i)
                break

        self.browser.execute_script(
            """
            return document.querySelector('[data-spotim-module="conversation"][data-spot-im-module-default-area="conversation"]').querySelector('div').shadowRoot.scrollTop = 0
            """
        )
        inner_conversation = self.browser.execute_script(
            """return document.querySelector('[data-spotim-module="conversation"][data-spot-im-module-default-area="conversation"]').querySelector('div').shadowRoot.querySelector('[data-spotim-module="conversation"][data-spot-im-module-default-area="conversation"]')"""
        )
        ul = inner_conversation.find_element_by_xpath('//ul[@class="spcv_messages-list"]')

        # get first level lis
        first_level_li_elements = ul.find_elements_by_css_selector('li:not(li li)')
        print("first_level_li_elements.len: ", len(first_level_li_elements))
        #
        nodes = []
        node_dicts = []
        i = 0
        # change it to define how may root comment to scrape
        max_first_level_comment = 5
        for li in first_level_li_elements:
            if i < max_first_level_comment:
                print("call recursive function for the comment tree with i: ", i)
                article = li.find_element_by_tag_name("article")
                article_div = article.find_element_by_class_name("spcv_threadingLine")
                # change maxdepth of reply to change how many depth to scrape
                node = self.recursive_function(article_div, depth=1, maxdepth=3)
                node_dict = self.convert_tree_node_to_dict(node=node)
                nodes.append(node)
                node_dicts.append(node_dict)
                # nodes.append(self.recursive_function(article_div))
            i = i + 1
        for node in nodes:
            print(node.username)
        print("Writing the comment tree into csv file")
        # Specify the text file path
        txt_file_path = 'output.txt'

        # Convert the nested dictionary to a JSON-formatted string
        json_data = json.dumps(node_dicts, indent=2)

        # Write the JSON-formatted string to the text file
        with open(txt_file_path, 'w') as txtfile:
            txtfile.write(json_data)

        print(f'Data has been written to {txt_file_path}')

        # print("print the nodes, nodes.len: ", len(nodes))
        # for node in nodes:
        #     print_tree(node=node)


browser = Browser(0).getBrowser()
scraper = FoxNewsScraper(browser=browser, depth=5)

url = "https://www.foxnews.com/entertainment/paulina-porizkova-58-poses-topless-painted-silver-makes-me-feel-strong?dicbo=v2-M8dSAZh"
# tiny urls of ismail
url1 = "https://www.foxnews.com/politics/biden-admin-confident-protect-americas-secrets-reports-china-spy-base-cuba"
# more level of replies
url1 = "https://www.foxnews.com/politics/hispanic-house-democrat-joins-republicans-calling-tougher-measures-border"
scraper.load_content(url1)


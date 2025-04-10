#  From Blocking to Breaking: Evaluating the Impact of Adblockers on Web Usability.

Recent years have seen a sharp rise in adblocker use, driven by increased web tracking and personalized ads. However, a significant issue for adblocker users is the web breakages they encounter, which worsens their browsing experience and often leads them to turn off their adblockers. Despite efforts by filter list maintainers to create rules that minimize these breakages, they remain a common issue. Our research aims to assess the extent of web breakages caused by adblocking on live sites using automated tools, attempting to establish a baseline for these disruptions. The study also outlines the challenges and limitations encountered when measuring web breakages in real-time. The current automated crawler's inability to consistently navigate a vast array of websites, combined with the unpredictable nature of web content, makes this research particularly difficult. We have identified several key findings related to web breakages in our preliminary study, which we intend to delve deeper into in future research.


## [Missing Resources](https://github.com/Mitchellzhou1/Ad-BlockerResearch/tree/Main/2.%20Resources%20(js))

![image](https://github.com/user-attachments/assets/d4b78c0d-a6d6-47bc-b86d-e38ef92319f8)

### Missing Resources:

**crawler.js**: 
1) 

**driver.mjs**


##  Broken Elements

![image](https://github.com/user-attachments/assets/05a2b176-c9ee-4f84-bff0-ba0e552830e7)

### Breakdown:

1) **divideChunks(websites, SIZE):** divides the website pool into `SIZE` lengthed batches.

   **Replay 0: Finding Elements. This mode must be set initially to find elements to interact with**
  
2) **processAllBatches(chunks, html_option, extn, replay):** Opens a control browser and scan the website for a list of interactable elements.

  - **find_elems():** Used to find the supported elements onthe page (dropdowns, buttons, links, logins, and input forms).

The scapper will store the outerHTML of the found element. e.g.,
```
{
//Buttons
  "https://mitchellzhou1.github.io/site/test.html": [
    "<button type=\"button\">Primary Button</button>",
    "<button type=\"button\" style=\"background-color: #28a745;\">Success Button</button>",
    "<button type=\"submit\">Login</button>"
  ],
...
//Links
  "https://mitchellzhou1.github.io/site/test.html": [
    "<a href=\"#home\">Home</a>",
    "<a href=\"#about\">About Us</a>",
    "<a href=\"#contact\">Contact</a>"
  ]
}
```
   **Replay 1: Interacting With Elements. This mode will only work if there are results from Replay 0**

2) **processAllBatches(chunks, html_option, extn, replay):** Opens a control browser and the browsers with the extensions.
   - **replay_initialize():** Will open the list of interactable elements from Replay 0 and find the elements based on the xpath.
   - **test_all_elements():** Once the element is found, the scrapper will preform the interactions. The results are storing `[initial_outer_html, outer_HTML_changed, local_DOM_changed, manual_change];`
**manual_change** is a flag used to see if there was any change in the DOM. There is high false-positives so these are flaged for manual review.

Results look like:
```
{
  "https://mitchellzhou1.github.io/site/test.html": [
    [
      "False - double checked",
      "<button type=\"button\">Primary Button</button>",
      false,
      false,
      true
    ],
    [
      "True",
      "<button type=\"button\" style=\"background-color: #28a745;\">Success Button</button>",
      false,
      false,
      true
    ],
  ]
}
```





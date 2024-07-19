Driver.prototype.scroll_to_bottom = async function() {
    // Define a timeout period in milliseconds
    const TIMEOUT_MS = 10000; // 10 seconds
  
    // Define the scrolling operation
    const scrollOperation = this.page.evaluate(async () => {
      await new Promise((resolve) => {
        const distance = 100; // Scroll distance
        const delay = 300;    // Delay between scrolls
  
        const scrollDown = () => {
          const totalHeight = document.body.scrollHeight;
          const currentPosition = window.scrollY + window.innerHeight;
  
          window.scrollBy(0, distance);
  
          if (currentPosition >= totalHeight) {
            resolve();
          } else {
            setTimeout(scrollDown, delay);
          }
        };
  
        scrollDown();
      });
    });
  
    // Define the timeout promise
    const timeoutPromise = new Promise((_, reject) => 
      setTimeout(() => reject(new Error('Scroll operation timed out')), TIMEOUT_MS)
    );
  
    // Race the scrolling operation against the timeout
    try {
      await Promise.race([scrollOperation, timeoutPromise]);
      console.log('Scrolling completed successfully.');
    } catch (error) {
      console.error(error.message);
      // Handle timeout case or perform other actions
      console.log('Handling timeout case...');
    }
  
    // Wait for 2 seconds
    await new Promise(resolve => setTimeout(resolve, 2000));
  
    // Scroll instantly to the top of the page
    await this.page.evaluate(() => window.scrollTo(0, 0));
  };
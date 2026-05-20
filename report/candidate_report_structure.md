• Résumé   
1\. Introduction –What is it about?   
• Context : some important combinatorial problems are hard to solve.  
the importance liyes in the big influence of the resolution of these problems on diverse domains, such as scheduling and project management and HR, finance, economics …ect, and the hardness of solving these problems in the other hand, lies in different aspects, mainly in the rarity of the capable and competent individuals (usally demands PHD or ceveral courses on combinatorial optimization).  
So being in this situation, where there’s a trivial concrete need, and a difficult, complex and costly way to respond to this need (recruting a phd\!), pushes to find other ways to solve, that are less costly, that is ‘automatic resolution’ by computational entitiy.  
Automating the resolution gives us the ability to bypass the previously mentioned problems plus …

Currently, Large Language models (LLMs), demonstrated strong reasoning capabilities, in different fields, which makes it the best suited computational entity for our study …ect

• Objectives : the objective of this tutorship is to investigate, experiment and respectively select the best possible suited LLM environment, to solve the most combinatorial problems possible, with the best possible metrics (resolution time, memory consumption …ect)

• Research question… : 

- How to exploit LLMs to solve combinatorial problems ?  
- How to optimise resolution performance ?  
- How to make the resolution process autoregressive and autonomous (resolution system rectifies itself by itself …ect)

2\. Préliminaires

- CSP as combinatorial problems  
  - definition  
  - Inference and resolution process   
  - Exécution and evaluation  
- LLM  
  - definition  
  - Important concepts (contexte window, interaction messages, attention …ect)  
  - Inference  
- Neuro-symbolic (state of the art ): in such systems, where LLMs are the reasoning engine, the problems to solve are usually considered as business logic (such as LLM chatbot for medical diagnoses : medical diagnoses here is just the business logic that have to be integrated properly into the LLM ecosystem)  
  - Prompt engineering  
    - model selection  
    - Agentic design  
  - Automatic refinement in neuro-symb  
    

2\. Materials and methods –How is the problem tackled?  

- the approach is combinating all three optimization techniques, forming a set of combinations, or what i like to call ‘configurations’, composed of one prompt engineering technique, one selected model, and one agentic design, and after experiment conduction, the best performing configuration will be selected.  
  \- Variating Prompting techniques (and show the theoretical limitations of it like context explosion ..ect) and how the candidate prompts were selected                                                                                                                                                                          
  \- Variating Delegation layers (and show the theoretical limitations of it like context explosion ..ect), and PDA explaination, and how the agentic design was made (based on the business logic and the usual expert’s resolution process …ect)                                                                                        
  \- Variating Model (with different model characteristics such as size, reasoning model or not ...ect \--   
- Refinement : for responding to the third research question, an iteration system was 

- Enumeration approach : the ‘selected model’ \* ‘prompting technique’ is simple to enumerate, and evaluate, but the integration of agentic design is bit more complexe to assess because it is an architectural design rather than just a numerated possible config, as a result to the complexity of each of the configuration parameters, the following method was mise en oeuvre :   
  - For each agentic delegation  
    - for each model selected  
      - for each prompting technique   
        - \[solve and iterate until solved or threshold attended\]

- measurements taken and their explanation (number of solved problems along with solver statistics …ect)
- Materials : intially kaggle and ngrok, then openRouter ; langsmith ; langgraph; choco solver ; java ; cps lib ...ect
• Tools, measurements, maths, approach…   
3\. Results –What has been done?   
• Developments (development after each experimentation step)  
• Results presentation and explanation   
4\. Conclusions –Which achievements?   
• Discuss results (explaining results)   
• Perspective and future work 
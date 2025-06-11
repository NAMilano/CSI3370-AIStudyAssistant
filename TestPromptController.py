import unittest
from unittest.mock import patch
from AIStudyAssistant import PromptController, GeminiServices, QuizQuestions, Flashcards, TopicExtractor

class TestPromptController(unittest.TestCase):
    def setUp(self):
        # create an instnace of PromptController before each test
        self.promptCon = PromptController()

    def tearDown(self):
        # clean up the instance after each test
        self.promptCon = None
    
    def testInit(self):
        # test the initialization of the other class objects in PromptController
        self.assertIsInstance(self.promptCon.geminiCall, GeminiServices)
        self.assertIsInstance(self.promptCon.quiz, QuizQuestions)
        self.assertIsInstance(self.promptCon.flash, Flashcards)
        self.assertIsInstance(self.promptCon.extractor, TopicExtractor)


    @patch('AIStudyAssistant.GeminiServices.call')
    def testGenerateQuizQuestions(self, mockCall):
        
        # mock the Gemini API call response for testing purposes
        mockCall.return_value = (
            "1. The _____ is the main heat source for the Earth.\tAnswer: Sun\n"
            "2. _____ is the hottest planet in the solar system.\tAnswer: Venus"
        )
        contents = "The Sun is the main heat source for the Earth. Venus is the hottest planet in the solar system."
        questions = self.promptCon.generateQuizQuestions(contents)

        # test that the questions are properly stored in the returned list
        self.assertEqual(len(questions), 2)

        # test that they are stored in the correct format and order 
        self.assertEqual(questions[0], ("1. The _____ is the main heat source for the Earth.", "Answer: Sun"))
        self.assertEqual(questions[1], ("2. _____ is the hottest planet in the solar system.", "Answer: Venus"))

        # test that there is no questions[2] since there are only 2 questions provided
        with self.assertRaises(IndexError):
            error = questions[2]
        
        # test that the correct error is thrown when no contents are passed 
        with self.assertRaises(ValueError) as context:
            self.promptCon.generateQuizQuestions("") 
        self.assertEqual(str(context.exception), "Error: Selected document has no contents")
        mockCall.assert_called_once()
    

    @patch('AIStudyAssistant.GeminiServices.call')
    def testGenerateFlashcards(self, mockCall):

        # mock the Gemini API call response for testing purposes
        mockCall.return_value = (
            "Why aren't strawberries berries?\tTheir seeds are on the outside.\n"
            "How many hearts do octopuses have?\tThree"
        )
        contents = "Strawberries are not berries because their seeds are on the outside. Octopuses are special because they have three hearts."
        cards = self.promptCon.generateFlashcards(contents)

        # test that the flashcards are properly stored in the returned list
        self.assertEqual(len(cards), 2)

        # test that they are stored in the correct format and order
        self.assertEqual(cards[0], ("Why aren't strawberries berries?", "Their seeds are on the outside."))
        self.assertEqual(cards[1], ("How many hearts do octopuses have?", "Three"))

        # test that there is no cards[2] since there are only 2 flashcards provided
        with self.assertRaises(IndexError):
            error = cards[2]

        # test that the correct error is thrown when no contents are passed 
        with self.assertRaises(ValueError) as context:
            self.promptCon.generateFlashcards("") 
        self.assertEqual(str(context.exception), "Error: Selected document has no contents")
        mockCall.assert_called_once()

    
    @patch('AIStudyAssistant.GeminiServices.call')
    def testExtractKeyTopics(self, mockCall):
        
        # mock the Gemini API call response for testing purposes
        mockCall.return_value = (
            "• Botanical Classifications - How plants are scientifically categorized, sometimes suprisingly.\n"
            "• Planetary Science - Comparitive characteristics of planets in our solar system."
        )
        contents = "Botanically, bananas are classified as berries, while strawberries are not because their seeds are on the outside. Venus is the hottest planet in the solar system, even though Mercury is closer to the sun."
        topics = self.promptCon.extractKeyTopics(contents)

        # test that the topics are properly returned 
        self.assertEqual(topics, "• Botanical Classifications - How plants are scientifically categorized, sometimes suprisingly.\n"
                         "• Planetary Science - Comparitive characteristics of planets in our solar system.")

        # test that the correct error is thrown when no contents are passed 
        with self.assertRaises(ValueError) as context:
            self.promptCon.extractKeyTopics("") 
        self.assertEqual(str(context.exception), "Error: Selected document has no contents")
        mockCall.assert_called_once()
        
    


if __name__ == '__main__':
    unittest.main()






































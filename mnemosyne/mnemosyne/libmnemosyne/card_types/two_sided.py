##############################################################################
#
# Two sided card type <Peter.Bienstman@UGent.be>
#
##############################################################################

import gettext
_ = gettext.gettext

from mnemosyne.libmnemosyne.card import Card
from mnemosyne.libmnemosyne.card_type import CardType
from mnemosyne.libmnemosyne.fact import Fact
from mnemosyne.libmnemosyne.config import config



##############################################################################
#
# TwoSided
#
#  q: question
#  a: answer
#
##############################################################################

class TwoSided(CardType):

    ##########################################################################
    #
    # __init__
    #
    ##########################################################################

    front_to_back = 0
    back_to_front = 1

    def __init__(self):
        
        CardType.__init__(self, id=1,
                          name=_("Regular card"),
                          can_be_unregistered=False)



    ##########################################################################
    #
    # generate_q
    #
    ##########################################################################

    def generate_q(self, fact, fact_view):

        if fact_view == TwoSided.front_to_back:
            return fact['q']
        elif fact_view == TwoSided.back_to_front:
            return fact['a']
        else:
            print 'Invalid subtype.'
            raise NameError


        
    ##########################################################################
    #
    # generate_a
    #
    ##########################################################################

    def generate_a(self, fact, fact_view):

        if fact_view == TwoSided.front_to_back:
            return fact['a']
        elif fact_view == TwoSided.back_to_front:
            return fact['q']
        else:
            print 'Invalid fact_view.'
            raise NameError

        

    ##########################################################################
    #
    # new_cards
    #
    ##########################################################################

    def new_cards(self, data):

        # Extract and remove data.

        grade          = data['grade']
        cat_names      = data['cat_names']
        add_vice_versa = data['add_vice_versa']
        
        del data['add_vice_versa']
        del data['grade']

        # Create fact.

        # TODO: add subtypes as a category?

        fact = Fact(data)
        fact.save()

        card = Card(grade=grade, card_type=self, fact=fact,
                    fact_view=TwoSided.front_to_back, cat_names=cat_names)
        card.save()

        if add_vice_versa:
            card_2 = Card(grade=grade, card_type=self, fact=fact,
                 fact_view=TwoSided.back_to_front, cat_names=cat_names,
                 id=card.id+'.inv')
            card_2.save()

        # TODO: drop the .inv suffix?

        self.widget.clear()

        return
    
        # TODO: add duplicate checking.
        
        ## Old code:

        orig_added = self.check_duplicates_and_add(grade,q,a,cat_names)
        rev_added = None

        if orig_added and add_vice_versa:
            rev_added = self.check_duplicates_and_add(grade,a,q,\
                                               cat_names,orig_added.id+'.inv')

        if add_vice_versa and orig_added and not rev_added:

            # Swap question and answer.

            self.question.setText(a)
            self.answer.setText(q)
            self.addViceVersa.setChecked(False)

        elif orig_added:

            # Clear the form to make room for new question.

            self.question.setText("")
            self.answer.setText("")



    ##########################################################################
    #
    # check_duplicates_and_add
    #
    # TODO: check how this needs to be changed when there are multiple
    # categories possible. Probably replace category by card types then.
    #
    ##########################################################################

    def check_duplicates_and_add(self, grade, q, a, cat_names, id=None):

        if config["check_duplicates_when_adding"] == True:

            # Find duplicate questions and refuse to add if duplicate
            # answers are found as well.

            allow_dif_cat = config["allow_duplicates_in_diff_cat"]

            same_questions = []

            for card in get_cards():
                if card.q == q:
                    if card.a == a:

                        if card.cat.name == cat_name or not allow_dif_cat:
                            QMessageBox.information(None,
                                                    _("Mnemosyne"),
                                _("Card is already in database.\n")\
                                .append(_("Duplicate not added.")),
                                _("&OK"))

                            return None

                    elif card.cat.name == cat_name or not allow_dif_cat:
                        same_questions.append(card)

            # Make a list of already existing answers for this question
            # and merge if the user wishes so.

            if len(same_questions) != 0:

                answers = a
                for i in same_questions:
                    answers += ' / ' + i.a

                status = QMessageBox.question(None,
                   _("Mnemosyne"),
                   _("There are different answers for this question:\n\n")\
                     .append(answers),
                   _("&Merge and edit"),
                   _("&Add as is"),
                   _("&Do not add"), 0, -1)

                if status == 0: # Merge and edit.

                    new_card = add_new_card(grade, q, a, cat_names, id)
                    self.update_combobox(cat_names)

                    for i in same_questions:
                        new_card.grade = min(new_card.grade, i.grade)
                        new_card.a += ' / ' + i.a
                        delete_card(i)

                    dlg = EditCardDlg(new_card, self)

                    dlg.exec_loop()

                    return new_card

                if status == 2: # Don't add.
                    return None

        new_card = add_new_card(grade, q, a, cat_names, id)
        self.update_combobox(cat_names)

        return new_card



    ##########################################################################
    #
    # update_cards
    #
    ##########################################################################

    def update_cards(self, data):

        pass

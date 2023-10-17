import unittest

from logics.classes.propositional import Formula, Inference
from logics.classes.propositional.proof_theories.metainferential_tableaux import MetainferentialTableauxStandard
from logics.instances.propositional.tableaux import (
    classical_tableaux_system, classical_indexed_tableaux_system, LP_tableaux_system, classical_constructive_tree_system
)
from logics.instances.propositional.metainferential_tableaux import metainferential_tableaux_rules
from logics.utils.solvers.tableaux import standard_tableaux_solver, indexed_tableaux_solver, metainferential_tableaux_solver
from logics.utils.parsers import classical_parser
from logics.utils.formula_generators.generators_biased import random_formula_generator
from logics.instances.propositional.languages import classical_infinite_language as cl_language
from logics.instances.propositional.languages import classical_infinite_language_noconditional as mvl_language
from logics.instances.propositional.many_valued_semantics import classical_mvl_semantics, LP_mvl_semantics


class TestTableauxSolver(unittest.TestCase):
    def test_some_inferences(self):
        conjunction_elimination = classical_parser.parse('p ∧ q / p')
        conditional_elimination = classical_parser.parse('p, p → q / q')
        modus_tollens = classical_parser.parse('~q, p → q / ~p')
        disjunction_elimination = classical_parser.parse('p ∨ q, p → r, q → r / r')
        double_negation = classical_parser.parse('~~p / p')
        de_morgan = classical_parser.parse('~(p ∨ q) / ~p ∧ ~q')
        de_morgan2 = classical_parser.parse('~(p ∧ q) / ~p ∨ ~q')
        conditional_negation = classical_parser.parse('~(p → q) / p')
        conditional_negation2 = classical_parser.parse('~(p → q) / ~q')
        negation_elimination = classical_parser.parse('p, ~p / ⊥')
        disjunctive_syllogism = classical_parser.parse('p ∨ q, ~p / q')
        disjunctive_syllogism2 = classical_parser.parse('p ∨ q, ~q / p')
        disjunctive_syllogism3 = classical_parser.parse('p ∨ ~q, q / p')
        conjunction_introduction = classical_parser.parse('p1 ∧ p2, p3 ∧ p4 / p2 ∧ p3')
        conditional_introduction = classical_parser.parse('p, q / p → q')
        disjunction_introduction = classical_parser.parse('p / p ∨ q')
        reductio = classical_parser.parse('p → (q ∧ ~q) / ~p')
        repetitions1 = classical_parser.parse('p / p ∧ p')
        repetitions2 = classical_parser.parse('/ p → p')

        # test_inferences = [conjunction_elimination, conditional_elimination, modus_tollens]
        test_inferences = [conjunction_elimination, conditional_elimination, modus_tollens, disjunction_elimination,
                           double_negation, de_morgan, de_morgan2, conditional_negation, conditional_negation2,
                           negation_elimination, disjunctive_syllogism, disjunctive_syllogism2, disjunctive_syllogism3,
                           conjunction_introduction, conditional_introduction, disjunction_introduction, reductio,
                           repetitions1, repetitions2]

        # Classical tableaux
        for inference in test_inferences:
            tableaux = standard_tableaux_solver.solve(inference, classical_tableaux_system)
            self.assertTrue(classical_tableaux_system.tree_is_closed(tableaux))
            try:
                self.assertTrue(classical_tableaux_system.is_correct_tree(tableaux, inference))
            except Exception as e:
                print(classical_parser.unparse(inference))
                tableaux.print_tree(classical_parser)
                raise e

        # Classical indexed tableaux
        for inference in test_inferences:
            tableaux = indexed_tableaux_solver.solve(inference, classical_indexed_tableaux_system)
            self.assertTrue(classical_indexed_tableaux_system.tree_is_closed(tableaux))
            try:
                self.assertTrue(classical_indexed_tableaux_system.is_correct_tree(tableaux, inference))
            except Exception as e:
                print(classical_parser.unparse(inference))
                tableaux.print_tree(classical_parser)
                raise e

    def test_with_generator(self):
        # Test with valid arguments
        for _ in range(500):
            inf = random_formula_generator.random_valid_inference(num_premises=2, num_conclusions=1,
                                                                  max_depth=3, atomics=['p', 'q', 'r'],
                                                                  language=cl_language,
                                                                  validity_apparatus=classical_mvl_semantics)

            # Non-indexed
            tableaux = standard_tableaux_solver.solve(inf, classical_tableaux_system)
            self.assertTrue(classical_tableaux_system.tree_is_closed(tableaux))
            # Indexed
            tableaux2 = indexed_tableaux_solver.solve(inf, classical_indexed_tableaux_system)
            self.assertTrue(classical_indexed_tableaux_system.tree_is_closed(tableaux2))

            # print('\nInference to solve:', classical_parser.unparse(inf))
            # tableaux.print_tree(classical_parser)
            try:
                self.assertTrue(classical_tableaux_system.is_correct_tree(tableaux, inf))
                self.assertTrue(classical_indexed_tableaux_system.is_correct_tree(tableaux2, inf))
            except Exception as e:
                print("ERROR WITH INFERENCE:", classical_parser.unparse(inf))
                # tableaux.print_tree(classical_parser)
                # correct, error_list = classical_tableaux_system.is_correct_tree(tableaux, inf, return_error_list=True)
                # print("ERROR LIST:", error_list)
                raise e

        # Test with invalid arguments
        for _ in range(500):
            invalid = False
            for x in range(100):
                inf = random_formula_generator.random_inference(num_premises=2, num_conclusions=1, max_depth=3,
                                                                atomics=['p', 'q', 'r'], language=cl_language)
                if not classical_mvl_semantics.is_valid(inf):
                    invalid = True
                if invalid:
                    break
                if x == 99:
                    print('Invalid argument not found')

            # Non-indexed
            tableaux = standard_tableaux_solver.solve(inf, classical_tableaux_system)
            self.assertFalse(classical_tableaux_system.tree_is_closed(tableaux))
            # Indexed
            tableaux2 = indexed_tableaux_solver.solve(inf, classical_indexed_tableaux_system)
            self.assertFalse(classical_indexed_tableaux_system.tree_is_closed(tableaux2))

            try:
                self.assertTrue(classical_tableaux_system.is_correct_tree(tableaux, inf))
                self.assertTrue(classical_indexed_tableaux_system.is_correct_tree(tableaux2, inf))
            except Exception as e:
                print("ERROR WITH INFERENCE:", classical_parser.unparse(inf))
                # tableaux.print_tree(classical_parser)
                # correct, error_list = classical_tableaux_system.is_correct_tree(tableaux, inf, return_error_list=True)
                # print("ERROR LIST:", error_list)
                raise e

    def test_mvl_tableaux(self):
        # Test with valid arguments
        for _ in range(100):
            inf = random_formula_generator.random_valid_inference(num_premises=2, num_conclusions=1,
                                                                    max_depth=3, atomics=['p', 'q', 'r'],
                                                                    language=mvl_language,
                                                                    validity_apparatus=LP_mvl_semantics)

            tableaux = indexed_tableaux_solver.solve(inf, LP_tableaux_system)
            self.assertTrue(LP_tableaux_system.tree_is_closed(tableaux))
            try:
                self.assertTrue(LP_tableaux_system.is_correct_tree(tableaux, inf))
            except Exception as e:
                print("ERROR WITH INFERENCE:", classical_parser.unparse(inf))
                tableaux.print_tree(classical_parser)
                correct, error_list = LP_tableaux_system.is_correct_tree(tableaux, inf, return_error_list=True)
                print("ERROR LIST:", error_list)
                raise e

        # Test with invalid arguments
        for _ in range(100):
            inf = random_formula_generator.random_invalid_inference(num_premises=2, num_conclusions=1,
                                                                      max_depth=3, atomics=['p', 'q', 'r'],
                                                                      language=mvl_language,
                                                                      validity_apparatus=LP_mvl_semantics)

            tableaux = indexed_tableaux_solver.solve(inf, LP_tableaux_system)
            self.assertFalse(LP_tableaux_system.tree_is_closed(tableaux))
            try:
                self.assertTrue(LP_tableaux_system.is_correct_tree(tableaux, inf))
            except Exception as e:
                print("ERROR WITH INFERENCE:", classical_parser.unparse(inf))
                tableaux.print_tree(classical_parser)
                correct, error_list = LP_tableaux_system.is_correct_tree(tableaux, inf, return_error_list=True)
                print("ERROR LIST:", error_list)
                raise e


class TestMetainferentialTableauxSolver(unittest.TestCase):
    def test_begin_tableaux(self):
        inference = Inference(premises=[Formula(['p']), Formula(['q'])], conclusions=[Formula(['p'])])
        initial_node = metainferential_tableaux_solver._begin_tableaux(inference, [{'1', 'i'}, {'1'}])
        self.assertEqual(initial_node.content, inference)
        self.assertEqual(initial_node.index, MetainferentialTableauxStandard([{'1', 'i'}, {'1'}], bar=True))
        self.assertEqual(len(initial_node.children), 0)

    def test_apply_rule(self):
        # inf0
        T, S = MetainferentialTableauxStandard({'1', 'i'}), MetainferentialTableauxStandard({'1'})
        subst_dict = {'Γ': [Formula(['p']), Formula(['q'])], 'Δ': [Formula(['p'])], 'X': T, 'Y': S}
        applied_rule = metainferential_tableaux_solver.apply_rule(cl_language, "inf0",
                                                                  metainferential_tableaux_rules['inf0'], subst_dict)
        # print(applied_rule.print_tree(classical_parser))
        """
        p, q / p, -[{'1', 'i'}, {'1'}]
        └── p, {'1', 'i'} (inf0)
            └── q, {'1', 'i'} (inf0)
                └── p, -{'1'} (inf0)
        """
        # First node: p, q / p, -TS
        self.assertEqual(applied_rule.content, Inference(premises=[Formula(['p']), Formula(['q'])],
                                                         conclusions=[Formula(['p'])]))
        self.assertEqual(applied_rule.index, MetainferentialTableauxStandard([T, S], bar=True))
        self.assertEqual(len(applied_rule.children), 1)
        # Second node: p, T
        child = applied_rule.children[0]
        self.assertEqual(child.content, Formula(['p']))
        self.assertEqual(child.index, T)
        self.assertEqual(len(child.children), 1)
        # Third node: q, T
        child = child.children[0]
        self.assertEqual(child.content, Formula(['q']))
        self.assertEqual(child.index, T)
        self.assertEqual(len(child.children), 1)
        # Third node: p, -S
        Sbar = MetainferentialTableauxStandard({'1'}, bar=True)
        child = child.children[0]
        self.assertEqual(child.content, Formula(['p']))
        self.assertEqual(child.index, Sbar)
        self.assertEqual(len(child.children), 0)

        # inf1
        applied_rule = metainferential_tableaux_solver.apply_rule(cl_language, "inf1",
                                                                  metainferential_tableaux_rules['inf1'], subst_dict)
        # print(applied_rule.print_tree(classical_parser))
        """
        p, q / p, [{'1', 'i'}, {'1'}]
        ├── p, -{'1', 'i'} (inf1)
        ├── q, -{'1', 'i'} (inf1)
        └── p, {'1'} (inf1)
        """
        # First node: p, q / p, TS
        self.assertEqual(applied_rule.content, Inference(premises=[Formula(['p']), Formula(['q'])],
                                                         conclusions=[Formula(['p'])]))
        self.assertEqual(applied_rule.index, MetainferentialTableauxStandard([T, S], bar=False))
        self.assertEqual(len(applied_rule.children), 3)
        # Second node: p, -T
        Tbar = MetainferentialTableauxStandard({'1', 'i'}, bar=True)
        child = applied_rule.children[0]
        self.assertEqual(child.content, Formula(['p']))
        self.assertEqual(child.index, Tbar)
        self.assertEqual(len(child.children), 0)
        # Third node: q, -T
        child = applied_rule.children[1]
        self.assertEqual(child.content, Formula(['q']))
        self.assertEqual(child.index, Tbar)
        self.assertEqual(len(child.children), 0)
        # Third node: p, S
        child = applied_rule.children[2]
        self.assertEqual(child.content, Formula(['p']))
        self.assertEqual(child.index, S)
        self.assertEqual(len(child.children), 0)

class TestConstructiveTreeSolver(unittest.TestCase):
    def test_constructive_tree_solver(self):
        # ~p
        tree = classical_constructive_tree_system.solve_tree(classical_parser.parse('~p'))
        self.assertEqual(tree.content, classical_parser.parse('~p'))
        self.assertEqual(len(tree.children), 1)
        self.assertEqual(tree.children[0].content, classical_parser.parse('p'))
        self.assertEqual(len(tree.children[0].children), 0)
        self.assertTrue(classical_constructive_tree_system.tree_is_closed(tree))

        # p ∧ ~q
        tree = classical_constructive_tree_system.solve_tree(classical_parser.parse('p ∧ ~q'))
        self.assertEqual(tree.content, classical_parser.parse('p ∧ ~q'))
        self.assertEqual(len(tree.children), 2)
        self.assertEqual(tree.children[0].content, classical_parser.parse('p'))
        self.assertEqual(len(tree.children[0].children), 0)
        self.assertEqual(tree.children[1].content, classical_parser.parse('~q'))
        self.assertEqual(len(tree.children[1].children), 1)
        self.assertEqual(tree.children[1].children[0].content, classical_parser.parse('q'))
        self.assertEqual(len(tree.children[1].children[0].children), 0)
        self.assertTrue(classical_constructive_tree_system.tree_is_closed(tree))

    def test_is_well_formed(self):
        self.assertTrue(classical_constructive_tree_system.is_well_formed(Formula(['~', ['~', ['p']]])))
        self.assertFalse(classical_constructive_tree_system.is_well_formed(Formula(['~', '~', ['p']])))
        # Needs further testing


if __name__ == '__main__':
    unittest.main()

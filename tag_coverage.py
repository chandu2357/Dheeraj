from collections import defaultdict

import dictdiffer

from test_helpers.mgs_validation_helpers.references.mgs_objects import \
    MobileResponse


class TagCoverage(object):
    scope = set()
    actual = defaultdict(dict)
    covered = defaultdict(dict)

    def update_actual(self, response, request_type):
        request_section = self.actual[request_type]
        ref_dict = MobileResponse(response).references.raw_data
        for reference_name, references_list in ref_dict.items():
            if reference_name not in self.scope:
                continue
            reference_section = request_section.get(reference_name, {})
            if not reference_section:
                request_section[reference_name] = set()
            for reference in references_list:
                request_section[reference_name].update(set(reference))

    def update_covered(self, request_type, reference_name, tag_name):
        self.scope.add(reference_name)
        request_section = self.covered[request_type]
        reference_section = request_section.get(reference_name, {})
        if not reference_section:
            request_section[reference_name] = set()
        request_section[reference_name].add(tag_name)

    def tag_report(self):
        actual_tags = self.actual
        covered_tags = self.covered
        dif_content = list((dictdiffer.diff(covered_tags, actual_tags)))
        report = {
            "References": self.scope,  # dif=('add', 'all.accounts', [(0, {'daysGain'})])
            "Uncovered": [f"{dif[1]} : {dif[2][0][1]}" for dif in dif_content if dif[0] == "add"],
            "Deprecated": [f"{dif[1]} : {dif[2][0][1]}" for dif in dif_content if dif[0] == "remove"]
        }
        return report


def tag_coverage_report(reporter):
    tag_report = MgsContext.references_tag.tag_report()
    newline = reporter.ensure_newline

    newline()
    reporter.section("Tag coverage report", sep="+", blue=True)

    headings = [f"References in scope: {tag_report['References']}",
                f"Not covered combinations of 'response.reference':"]

    for header in headings:
        reporter.line(header)
    for line in tag_report['Uncovered']:
        reporter.line(line)
    newline()

    reporter.line(f"This tags have tests,"
                  f" but no more such tag in actual responses:")
    for line in tag_report["Deprecated"]:
        reporter.line(line)
    newline()


class MgsContext:
    node_testing = False
    references_tag = TagCoverage()

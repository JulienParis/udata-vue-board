<template>
  <div class="issue_update">

    <b-breadcrumb
      class="mb-5"
      :items="crumbs">
    </b-breadcrumb>

    <h2>
      Issue update
    </h2>
    <div>
      from :
      <span v-if="issueRequest">
        <a :href="issueRequest" target="_blank">
          JSON
        </a>
        |
        <a :href="issue.url" target="_blank">
          datagouv issue page
        </a>
      </span>
      <span v-else>
        {{ getOperationId }}
      </span>
    </div>

    <br>

    <!-- DISPLAY ISSUE -->
    <IssueCard
      :cardTitle="`issue n° ${issueId}`"
      :cardFooter="undefined"
      :issueData="issue"
      :issueId="issueId"
      height="800px"
      width="600px"
    >
    </IssueCard>

  </div>
</template>

<script>
import IssueCard from '@/components/issues/IssueCard.vue'
import { mapState } from 'vuex'

export default {
  name: 'IssueUpdate',
  components: {
    IssueCard
  },
  data () {
    return {
      isLoading: false,
      getOperationId: 'get_issue',
      putOperationId: 'update_issue',
      issueId: this.$route.params.id,
      issueRequest: undefined,
      issue: undefined,
      crumbs: [
        {
          text: 'Home',
          to: '/'
        },
        {
          text: 'Issues',
          to: '/issues'
        },
        {
          text: '...', // this.$route.params.id,
          active: true
        }
      ]
    }
  },
  created () {
    this.getIssue()
  },
  watch: {},
  computed: {
    ...mapState({
      log: (state) => state.log
    })
  },
  methods: {
    getIssue () {
      const API = this.$APIcli
      console.log('-V- IssueUpdate > methods > getIssue > API :', API)
      const params = { id: this.issueId }
      this.isLoading = true
      API._request(this.getOperationId, { params }).then(
        results => {
          console.log('-V- IssueUpdate > methods > getIssue > results :', results)
          console.log('-V- IssueUpdate > methods > getIssue > results.body :', results.body)
          this.issueRequest = results.url
          this.issue = results.body
          this.crumbs[2].text = `${this.issue.title}`
          this.isLoading = false
        },
        reason => {
          console.error(`failed on api call: ${reason}`)
          this.isLoading = false
        }
      )
    }
  }
}

</script>
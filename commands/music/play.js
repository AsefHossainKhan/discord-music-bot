const { SlashCommandBuilder } = require('@discordjs/builders')
const { EmbedBuilder } = require('discord.js')
const { QueryType, useMainPlayer } = require('discord-player')
const { YoutubeiExtractor } = require("discord-player-youtubei")

module.exports = {
  data: new SlashCommandBuilder().setName('play').
    setDescription('Play songs from YouTube').
    addSubcommand((subcommand) =>
      subcommand.setName('search').
        setDescription('Searches for a song and plays it').
        addStringOption((option) =>
          option.setName('searchterms').
            setDescription('search keywords').
            setRequired(true),
        ),
    ).
    addSubcommand((subcommand) =>
      subcommand.setName('playlist').
        setDescription('Plays a playlist from YT playlist link').
        addStringOption((option) =>
          option.setName('url').
            setDescription('the playlist\'s url').
            setRequired(true),
        ),
    ).
    addSubcommand((subcommand) =>
      subcommand.setName('link').
        setDescription('Plays a single song from the YT link/url').
        addStringOption((option) =>
          option.setName('url').
            setDescription('the song\'s url').
            setRequired(true),
        ),
    ),
  async execute(interaction) {
    const player = useMainPlayer()

    const youtubeAuth = "access_token=ya29.a0AcM612w8RC5yRXptev6YRPwjTQnOav7ab4QpZlj0l3JSfv0IihlHJl_mMyAdlH_0Vs9TDIvR7zyi5uPQdH6mnRXwrNBFw1jOvFleBOy1GfGCwszH1OQdk5vsVRVo8Vvmo5rU3F8kqlFcj0V0k_qhUAUfJfxOrAoBe6orY8yRPsRLn1l2aCgYKAScSARESFQHGX2Mi8vc4P3PbTAT5IH6RBv0fXQ0183; refresh_token=1//0gsQEZhQaboqMCgYIARAAGBASNwF-L9IrLjwJGIrMdiCfWzZ8buRzetx8hQi8N842rL0hphgbk-O3y-mcZ7kIMaO9jkAVSn0tijs; scope=https://www.googleapis.com/auth/youtube-paid-content https://www.googleapis.com/auth/youtube; token_type=Bearer; expiry_date=2024-08-12T12:00:51.177Z";
    player.extractors.register(YoutubeiExtractor, {
      authentication: youtubeAuth
    })

    await player.extractors.loadDefault((ext) => !['YouTubeExtractor'].includes(ext));

    // Make sure the user is inside a voice channel
    if (!interaction.member.voice.channel)
      return interaction.reply(
        'You need to be in a Voice Channel to play a song.',
      )

    await interaction.deferReply()

    // Create a play queue for the server
    const queue = await player.nodes.create(interaction.guild, {
      metadata: {
        channel: interaction.channel,
        client: interaction.guild.members.me,
        requestedBy: interaction.user,
      },
      selfDeaf: true,
      volume: 100,
      leaveOnEmpty: true,
      leaveOnEmptyCooldown: 300000,
      leaveOnEnd: true,
      leaveOnEndCooldown: 300000,
    })

    // Wait until you are connected to the channel
    if (!queue.connection)
      await queue.connect(interaction.member.voice.channel)

    let embed = new EmbedBuilder()

    if (interaction.options.getSubcommand() === 'link') {
      let url = interaction.options.getString('url')

      // Search for the song using the discord-player
      const result = await player.search(url, {
        requestedBy: interaction.user,
        searchEngine: QueryType.YOUTUBE_VIDEO,
      })

      // finish if no tracks were found
      if (result.tracks.size === 0) return interaction.reply('No results')

      // Add the track to the queue
      const song = result.tracks[0]
      await queue.addTrack(song)
      embed.setDescription(
        `**[${song.title}](${song.url})** has been added to the Queue`,
      ).
        setThumbnail(song.thumbnail).
        setFooter({ text: `Duration: ${song.duration}` })
    } else if (interaction.options.getSubcommand() === 'playlist') {
      // Search for the playlist using the discord-player
      let url = interaction.options.getString('url')
      const result = await player.search(url, {
        requestedBy: interaction.user,
        searchEngine: QueryType.YOUTUBE_PLAYLIST,
      })

      if (result.tracks.size === 0)
        return interaction.reply(`No playlists found with ${url}`)

      // Add the tracks to the queue
      const playlist = result.playlist
      await queue.addTrack(result.tracks)
      embed.setDescription(
        `**${result.tracks.length} songs from [${playlist.title}](${playlist.url})** have been added to the Queue`,
      ).setThumbnail(playlist.thumbnail.url)
    } else if (interaction.options.getSubcommand() === 'search') {
      // Search for the song using the discord-player
      let url = interaction.options.getString('searchterms')
      const result = await player.search(url, {
        requestedBy: interaction.user,
        searchEngine: QueryType.YOUTUBE,
      })

      // finish if no tracks were found
      if (result.tracks.length === 0)
        return interaction.editReply('No results')

      // Add the track to the queue
      const song = result.tracks[0]
      await queue.addTrack(song)
      embed.setDescription(
        `**[${song.title}](${song.url})** has been added to the Queue`,
      ).
        setThumbnail(song.thumbnail).
        setFooter({ text: `Duration: ${song.duration}` })
    }

    // Play the song
    if (!queue.node.isPlaying()) await queue.node.play()

    // Respond with the embed containing information about the player
    await interaction.editReply({
      embeds: [embed],
    })
  },
}
